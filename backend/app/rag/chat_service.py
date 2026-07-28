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

        print("Retrieved documents:")
        for result in results:
            title = self._result_title(result)
            print("--------------------------------")
            print(title)
            print(result.score)
            print(result.content)

        prompt = self.prompt_builder.build(question, results)

        print("=" * 80)
        print("PROMPT SENT TO LLM")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        answer = self.llm.chat(prompt)
        return answer, results

    def _result_title(self, result: SearchResult) -> str:
        metadata = result.metadata
        if "title" in metadata:
            return str(metadata["title"])

        round_name = metadata.get("round", "Match")
        team_a = metadata.get("team_a", "Unknown")
        team_b = metadata.get("team_b", "Unknown")
        return f"{round_name}: {team_a} vs {team_b}"
