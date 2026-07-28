from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.llm.embedding_client import EmbeddingClient
from app.llm.ollama_client import OllamaClient
from app.rag.chat_service import RAGChatService
from app.rag.prompt_builder import PromptBuilder
from app.rag.query_service import QueryService
from app.rag.vector_repository import VectorRepository

app = FastAPI(
    title="World Cup RAG API",
    version="0.1.0",
)

query_service = QueryService(
    embedding_client=EmbeddingClient(),
    repository=VectorRepository(collection_name="worldcup2022"),
)

rag_service = RAGChatService(
    query_service=query_service,
    prompt_builder=PromptBuilder(),
    llm=OllamaClient(),
)


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    title: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)


class OpenAIChatMessage(BaseModel):
    role: str
    content: str


class OpenAIChatCompletionRequest(BaseModel):
    model: str = "worldcup-rag"
    messages: list[OpenAIChatMessage]


def _sources_from_results(results) -> list[Source]:
    sources: list[Source] = []
    for result in results:
        team_a = result.metadata.get("team_a", "Unknown")
        team_b = result.metadata.get("team_b", "Unknown")
        round_name = result.metadata.get("round", "Match")
        sources.append(
            Source(
                title=f"{round_name}: {team_a} vs {team_b}",
                score=round(float(result.score), 4),
            )
        )
    return sources


def _latest_user_message(messages: list[OpenAIChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content
    raise ValueError("No user message found in request")


@app.get("/")
def root():
    return {"message": "World Cup RAG API is running!"}


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "worldcup-rag",
                "object": "model",
                "created": int(datetime.now(timezone.utc).timestamp()),
                "owned_by": "worldcuprag",
            }
        ],
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, results = rag_service.answer(request.message)
    return ChatResponse(
        answer=answer,
        sources=_sources_from_results(results),
    )


@app.post("/v1/chat/completions")
def openai_chat_completions(request: OpenAIChatCompletionRequest):
    question = _latest_user_message(request.messages)
    answer, _results = rag_service.answer(question)

    return {
        "id": f"chatcmpl-{uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(datetime.now(timezone.utc).timestamp()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer,
                },
                "finish_reason": "stop",
            }
        ],
    }
