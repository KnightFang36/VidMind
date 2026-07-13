"""End-to-end RAG orchestration (sync + streaming)."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.services.cache import answer_cache, retrieval_cache, TTLCache
from app.services.guardrails import (
    INSUFFICIENT_CONTEXT_MESSAGE,
    build_citations,
    has_sufficient_evidence,
)
from app.services.indexing import VideoIndexService
from app.services.memory import (
    ConversationMemory,
    build_standalone_question,
)
from app.services.retrieval import adaptive_top_k, build_advanced_retriever

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that answers questions using ONLY the "
            "provided video transcript context.\n"
            "Rules:\n"
            "1. If the answer is not in the context, reply exactly: "
            f"\"{INSUFFICIENT_CONTEXT_MESSAGE}\"\n"
            "2. Never invent facts not supported by the context.\n"
            "3. When helpful, cite the supporting moment using [start] "
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

    def _retrieve(
        self, video_id: str, query: str, history: Optional[list[dict]]
    ) -> tuple[ChatGroq, str, list[Document]]:
        """Retrieve documents with full pipeline."""
        llm = _get_llm(streaming=False)

        memory = _build_memory(history)
        standalone = build_standalone_question(llm, memory, query)

        self._video_index.ensure_indexed(video_id)
        k_sub, k_final = adaptive_top_k(standalone)

        cache_key = TTLCache.make_key(video_id, standalone, k_sub, k_final)
        cached_docs = retrieval_cache.get(cache_key)
        if cached_docs is not None:
            return llm, standalone, cached_docs

        base = self._video_index.get_hybrid_retriever(video_id, k_sub=k_sub)
        retriever = build_advanced_retriever(base, llm, k_final, use_multi_query=True)
        child_docs = retriever.invoke(standalone)

        parents = self._video_index.get_parents(video_id, child_docs)
        context_docs = parents or child_docs

        retrieval_cache.set(cache_key, context_docs)
        return llm, standalone, context_docs

    def answer(
        self, video_id: str, query: str, history: Optional[list[dict]] = None
    ) -> RagAnswer:
        """Non-streaming answer."""
        llm, standalone, context_docs = self._retrieve(video_id, query, history)

        ans_key = TTLCache.make_key("answer", video_id, standalone)
        cached = answer_cache.get(ans_key)
        if cached is not None:
            return cached

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

    def answer_stream(
        self, video_id: str, query: str, history: Optional[list[dict]] = None
    ) -> Iterator[dict]:
        """Stream answer tokens in real-time."""
        _, standalone, context_docs = self._retrieve(video_id, query, history)

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
