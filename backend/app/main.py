from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.ingest.chunker import Chunker
from app.ingest.document_builder import DocumentBuilder
from app.ingest.indexer import Indexer
from app.ingest.parser import WorldCupParser
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

embedding_client = EmbeddingClient()
prompt_builder = PromptBuilder()
llm = OllamaClient()

active_year = 2022
repository = VectorRepository(collection_name=f"worldcup{active_year}")
query_service = QueryService(
    embedding_client=embedding_client,
    repository=repository,
)
rag_service = RAGChatService(
    query_service=query_service,
    prompt_builder=prompt_builder,
    llm=llm,
)


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    title: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)


class IndexResponse(BaseModel):
    year: int
    collection: str
    matches: int
    documents: int
    chunks: int
    activated: bool


class OpenAIChatMessage(BaseModel):
    role: str
    content: str


class OpenAIChatCompletionRequest(BaseModel):
    model: str = "worldcup-rag"
    messages: list[OpenAIChatMessage]


def _project_root() -> Path:
    # backend/app/main.py -> backend -> project root (local)
    # /app/app/main.py -> /app (docker backend root)
    backend_root = Path(__file__).resolve().parents[1]
    project_root = backend_root.parent
    if (project_root / "data" / "raw").exists():
        return project_root
    return backend_root


def _resolve_year_folder(year: int) -> Path:
    root = _project_root()
    candidates = [
        root / "data" / "raw" / str(year),
        root / "data" / "worldcup.json" / str(year),
        Path("/data/raw") / str(year),
    ]

    for folder in candidates:
        if (folder / "worldcup.json").exists():
            return folder

    raise HTTPException(
        status_code=404,
        detail=f"No World Cup data found for year {year}",
    )


def _activate_year(year: int) -> None:
    global active_year, repository, query_service, rag_service

    active_year = year
    repository = VectorRepository(collection_name=f"worldcup{year}")
    query_service = QueryService(
        embedding_client=embedding_client,
        repository=repository,
    )
    rag_service = RAGChatService(
        query_service=query_service,
        prompt_builder=prompt_builder,
        llm=llm,
    )


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
    return {
        "message": "World Cup RAG API is running!",
        "active_year": active_year,
        "collection": f"worldcup{active_year}",
    }


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


@app.post("/index/{year}", response_model=IndexResponse)
def index_year(year: int, activate: bool = True):
    folder = _resolve_year_folder(year)
    collection_name = f"worldcup{year}"

    indexer = Indexer(
        parser=WorldCupParser(str(folder)),
        builder=DocumentBuilder(),
        chunker=Chunker(),
        embedding_client=embedding_client,
        repository=VectorRepository(collection_name=collection_name),
    )

    stats = indexer.index(str(folder))

    if activate:
        _activate_year(year)

    return IndexResponse(
        year=stats["year"],
        collection=collection_name,
        matches=stats["matches"],
        documents=stats["documents"],
        chunks=stats["chunks"],
        activated=activate,
    )


@app.post("/activate/{year}")
def activate_year(year: int):
    _activate_year(year)
    return {
        "active_year": active_year,
        "collection": f"worldcup{active_year}",
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
