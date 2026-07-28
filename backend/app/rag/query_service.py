from app.llm.embedding_client import EmbeddingClient
from app.models.search_result import SearchResult
from app.rag.vector_repository import VectorRepository


class QueryService:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        repository: VectorRepository,
    ):
        self.embedding_client = embedding_client
        self.repository = repository

    def query(self, question: str, top_k: int = 5) -> list[SearchResult]:
        embedding = self.embedding_client.embed(question)
        return self.repository.search(embedding, top_k=top_k)
