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


def _format_documents(documents) -> str:
    return "\n\n".join(document.page_content for document in documents)


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    return ChatGroq(model=get_settings().llm_model, temperature=0.7)


class RagService:
    def __init__(self, video_index: VideoIndexService) -> None:
        self._video_index = video_index

    def answer(self, video_id: str, question: str) -> str:
        retriever = self._video_index.get_retriever(video_id)
        context = itemgetter("question") | retriever | RunnableLambda(_format_documents)
        chain = (
            RunnableParallel(
                context=context,
                question=itemgetter("question") | RunnablePassthrough(),
            )
            | PROMPT
            | get_llm()
            | StrOutputParser()
        )
        return chain.invoke({"question": question})
