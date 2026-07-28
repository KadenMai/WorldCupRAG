from app.llm.embedding_client import EmbeddingClient
from app.rag.query_service import QueryService
from app.rag.vector_repository import VectorRepository


QUESTIONS = [
    "Who won the World Cup?",
    "Who beat France?",
    "Messi final goals",
    "Lusail Stadium final",
    "Penalty shootout Argentina",
]


def main() -> None:
    query_service = QueryService(
        embedding_client=EmbeddingClient(),
        repository=VectorRepository(collection_name="worldcup2022"),
    )

    for question in QUESTIONS:
        print("=" * 60)
        print(f"Q: {question}")
        print("=" * 60)

        results = query_service.query(question, top_k=5)

        for i, result in enumerate(results, start=1):
            title = f"{result.metadata.get('round', 'Unknown')}: {result.metadata.get('team_a')} vs {result.metadata.get('team_b')}"
            print(f"\n[{i}] score={result.score:.4f}")
            print(f"    {title}")
            print(f"    {result.content[:200]}...")

        print()


if __name__ == "__main__":
    main()
