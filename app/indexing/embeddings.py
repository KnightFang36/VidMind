from textSplitting import chunks    
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

vectorstore = FAISS.from_documents(chunks, embeddings)

print(vectorstore.index_to_docstore_id)