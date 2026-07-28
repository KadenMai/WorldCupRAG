from app.llm.ollama_client import OllamaClient
from app.models.search_result import SearchResult
from app.rag.prompt_builder import PromptBuilder
from app.rag.query_service import QueryService


class RAGChatService:
    def __init__(
        self,
        query_service: QueryService,
        prompt_builder: PromptBuilder,
        llm: OllamaClient,
        top_k: int = 5,
    ):
        self.query_service = query_service
        self.prompt_builder = prompt_builder
        self.llm = llm
        self.top_k = top_k

    def answer(self, question: str) -> tuple[str, list[SearchResult]]:
        results = self.query_service.query(question, top_k=self.top_k)
        prompt = self.prompt_builder.build(question, results)
        answer = self.llm.chat(prompt)
        return answer, results
