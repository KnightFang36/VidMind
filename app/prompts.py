"""Prompt templates used by the application."""

from langchain_core.prompts import PromptTemplate


prompt= PromptTemplate(
    template="You are a helpful assistant that answers questions based on the context provided. If the answer is not contained within the context, say 'I don't know.'\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:",
    input_variables=["context", "question"]
)

# final_prompt=prompt.invoke({"context": context_text, "question": query})

