from dataclasses import dataclass
from functools import lru_cache
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq

from backend.app.core.config import get_settings
from backend.app.services.indexing import VideoIndexService

PROMPT = PromptTemplate(
    template=(
        "You are a helpful assistant that answers questions using only the provided "
        "video transcript context. If the answer is not in the context, say that you "
        "don't know.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    ),
    input_variables=["context", "question"],
)


@dataclass
class RagAnswer:
    answer: str
    sources: list[dict]


def _format_documents(documents) -> str:
    return "\n\n".join(document.page_content for document in documents)


def _serialize_documents(documents) -> list[dict]:
    return [
        {
            "content": document.page_content,
            "chunk_index": document.metadata.get("chunk_index"),
        }
        for document in documents
    ]


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    return ChatGroq(model=get_settings().llm_model, temperature=0.7)


def _build_chain(retriever):
    answer_chain = (
        {
            "context": RunnableLambda(lambda x: _format_documents(x["context"])),
            "question": itemgetter("question"),
        }
        | PROMPT
        | get_llm()
        | StrOutputParser()
    )

    return (
        RunnableParallel(
            context=itemgetter("query") | retriever,
            question=itemgetter("query"),
        )
        | RunnablePassthrough.assign(answer=answer_chain)
    )


class RagService:
    def __init__(self, video_index: VideoIndexService) -> None:
        self._video_index = video_index

    def answer(self, video_id: str, query: str) -> RagAnswer:
        self._video_index.ensure_indexed(video_id)
        retriever = self._video_index.get_retriever(video_id)
        chain = _build_chain(retriever)
        result = chain.invoke({"query": query})

        return RagAnswer(
            answer=result["answer"],
            sources=_serialize_documents(result["context"]),
        )