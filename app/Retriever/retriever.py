"""Vector search and document retrieval."""

from app.indexing.embeddings import vectorstore
from app.query import query

retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

retreived_docs=retriever.invoke(query)

context_text="\n\n".join([doc.page_content for doc in retreived_docs])

