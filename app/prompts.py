"""Prompt templates used by the application."""

from langchain.prompts import prompt_template

prompt= prompt_template (
    template="You are a helpful assistant that answers questions based on the context provided. If the answer is not contained within the context, say 'I don't know.'\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:",
    input_variables=["context", "question"]
)
