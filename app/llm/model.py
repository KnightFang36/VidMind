from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.prompts import final_prompt

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.7
)

answer=llm.invoke(final_prompt)
print(answer.content)
