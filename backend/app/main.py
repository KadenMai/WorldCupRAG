from fastapi import FastAPI
from pydantic import BaseModel

from app.llm.ollama_client import OllamaClient

app = FastAPI(
    title="World Cup RAG API",
    version="0.1.0"
)

llm = OllamaClient()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/")
def root():
    return {"message": "World Cup RAG API is running!"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = llm.chat(request.message)
    return ChatResponse(answer=answer)
