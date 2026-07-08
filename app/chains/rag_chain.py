from app.Retriever.retriever import retriever
from operator import itemgetter 
from langchain_core.runnables import RunnableSequence,RunnableParallel,RunnablePassthrough,RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from app.query import query
from app.prompts import prompt
from app.llm.model import llm


def format_docs(retrieved_docs):
    context_text="\n\n".join([doc.page_content for doc in retrieved_docs])
    return context_text


parallel_chain=RunnableParallel(
    {
        "context": itemgetter("question") | retriever | RunnableLambda(format_docs),
        "question": itemgetter("question") | RunnablePassthrough()
    }
)

parser=StrOutputParser()

main_chain=parallel_chain | prompt| llm | parser



result=main_chain.invoke({"question": query})
print(result)