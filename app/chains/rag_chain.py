from app.Retriever.retriever import retriever

from langchain_core.runnables import RunnableSequence,RunnableParallel,RunnablePassthrough,RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from app.query import query


def format_docs(retrieved_docs):
    context_text="\n\n".join([doc.page_content for doc in retrieved_docs])
    return context_text


parallel_chain=RunnableParallel(
    {
        "context": retriever | RunnableLambda(format_docs),
        "question":RunnablePassthrough()
    }
)

result=parallel_chain.invoke(query)
print(result)