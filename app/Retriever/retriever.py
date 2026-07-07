"""Vector search and document retrieval."""

from app.indexing.embeddings import vectorstore

retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

retreived_docs=retriever.invoke("What is deepmind ?")
print(retreived_docs)