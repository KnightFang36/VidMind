# services/rag.py
#
# End-to-end modern RAG orchestration. Pipeline for every question:
#
#   history + question
#        -> Standalone Question Generator          (memory.py, #10)
#        -> ensure hybrid + parent index           (indexing.py, #3/#8)
#        -> Adaptive Top-K                          (retrieval.py, #11)
#        -> Hybrid Retrieval (FAISS + BM25)         (indexing.py, #3)
#        -> MultiQuery + Cross-Encoder Rerank
#           + Context Compression                   (retrieval.py, #7)
#        -> Parent Document Retrieval               (indexing.py, #8)
#        -> Hallucination Guard                      (guardrails.py, #12)
#        -> Prompt + LLM (+ streaming)              (this file, #19)
#        -> Citation Builder w/ timestamps          (guardrails.py)
#   Retrieval + answer results are cached           (cache.py, #18)

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.app.core.config import get_settings
from backend.app.services.cache import answer_cache, retrieval_cache, TTLCache
from backend.app.services.guardrails import (
    INSUFFICIENT_CONTEXT_MESSAGE,
    build_citations,
    has_sufficient_evidence,
)
from backend.app.services.indexing import VideoIndexService
from backend.app.services.memory import (
    ConversationMemory,
    build_standalone_question,
)
from backend.app.services.retrieval import adaptive_top_k, build_advanced_retriever

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that answers questions using ONLY the "
            "provided video transcript context.\n"
            "Rules:\n"
            "1. If the answer is not in the context, reply exactly: "
            f"\"{INSUFFICIENT_CONTEXT_MESSAGE}\"\n"
            "2. Never invent facts that are not supported by the context.\n"
            "3. When helpful, cite the supporting moment using its [start] "
            "timestamp shown in the context.\n"
            "4. Be concise and accurate.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"),
    ]
)


@dataclass
class RagAnswer:
    answer: str
    sources: list[dict] = field(default_factory=list)
    standalone_question: str = ""
    grounded: bool = True


def _get_llm(streaming: bool = False) -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.llm_model,
        temperature=0.3,
        api_key=settings.groq_api_key,
        streaming=streaming,
    )


def _format_context(documents: list[Document]) -> str:
    parts = []
    for doc in documents:
        start = doc.metadata.get("start", 0.0)
        parts.append(f"[start={start}s]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _build_memory(history: Optional[list[dict]]) -> ConversationMemory:
    memory = ConversationMemory()
    for turn in history or []:
        role = (turn.get("role") or "").lower()
        content = turn.get("content") or ""
        if not content:
            continue
        if role in ("user", "human"):
            memory.add_user(content)
        elif role in ("assistant", "ai", "bot"):
            memory.add_assistant(content)
    return memory


class RagService:
    def __init__(self, video_index: VideoIndexService) -> None:
        self._video_index = video_index

    # ------------------------------------------------------------------
    # Shared retrieval path (memory -> retrieve -> parents)
    # ------------------------------------------------------------------
    def _retrieve(
        self, video_id: str, query: str, history: Optional[list[dict]]
    ) -> tuple[ChatGroq, str, list[Document]]:
        llm = _get_llm(streaming=False)

        memory = _build_memory(history)
        # #10 Conversation Memory: condense history + question into a standalone one.
        standalone = build_standalone_question(llm, memory, query)

        self._video_index.ensure_indexed(video_id)
        k_sub, k_final = adaptive_top_k(standalone)

        cache_key = TTLCache.make_key(video_id, standalone, k_sub, k_final)
        cached_docs = retrieval_cache.get(cache_key)
        if cached_docs is not None:
            return llm, standalone, cached_docs

        base = self._video_index.get_hybrid_retriever(video_id, k_sub=k_sub)
        retriever = build_advanced_retriever(base, llm, k_final)
        child_docs = retriever.invoke(standalone)

        # Parent Document Retrieval — swap children for their richer parents.
        parents = self._video_index.get_parents(video_id, child_docs)
        context_docs = parents or child_docs

        retrieval_cache.set(cache_key, context_docs)
        return llm, standalone, context_docs

    # ------------------------------------------------------------------
    # Non-streaming answer
    # ------------------------------------------------------------------
    def answer(
        self, video_id: str, query: str, history: Optional[list[dict]] = None
    ) -> RagAnswer:
        llm, standalone, context_docs = self._retrieve(video_id, query, history)

        # Answer cache (only meaningful for repeat questions on the same video).
        ans_key = TTLCache.make_key("answer", video_id, standalone)
        cached = answer_cache.get(ans_key)
        if cached is not None:
            return cached

        # #12 Hallucination Guard
        if not has_sufficient_evidence(standalone, context_docs):
            result = RagAnswer(
                answer=INSUFFICIENT_CONTEXT_MESSAGE,
                sources=[],
                standalone_question=standalone,
                grounded=False,
            )
            answer_cache.set(ans_key, result)
            return result

        chain = PROMPT | llm | StrOutputParser()
        answer_text = chain.invoke(
            {"context": _format_context(context_docs), "question": standalone}
        )

        result = RagAnswer(
            answer=answer_text,
            sources=build_citations(context_docs),
            standalone_question=standalone,
            grounded=True,
        )
        answer_cache.set(ans_key, result)
        return result

    # ------------------------------------------------------------------
    # #19 Streaming answer
    # ------------------------------------------------------------------
    def answer_stream(
        self, video_id: str, query: str, history: Optional[list[dict]] = None
    ) -> Iterator[dict]:
        """
        Yield server-sent-event-friendly dicts:
          {"type": "sources", "data": [...]}      (once, up front)
          {"type": "token",   "data": "..."}      (many)
          {"type": "done"}                          (once)
        """
        _, standalone, context_docs = self._retrieve(video_id, query, history)

        # #12 Hallucination Guard — stream the refusal instead of hallucinating.
        if not has_sufficient_evidence(standalone, context_docs):
            yield {"type": "sources", "data": []}
            yield {"type": "token", "data": INSUFFICIENT_CONTEXT_MESSAGE}
            yield {"type": "done", "grounded": False}
            return

        yield {"type": "sources", "data": build_citations(context_docs)}

        stream_llm = _get_llm(streaming=True)
        chain = PROMPT | stream_llm | StrOutputParser()
        for chunk in chain.stream(
            {"context": _format_context(context_docs), "question": standalone}
        ):
            if chunk:
                yield {"type": "token", "data": chunk}

        yield {"type": "done", "grounded": True}