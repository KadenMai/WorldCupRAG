from app.llm.embedding_client import EmbeddingClient
from app.rag.vector_repository import VectorRepository


repo = VectorRepository(collection_name="worldcup2022-test")
repo.delete_collection()

client = EmbeddingClient()

texts = [
    "Argentina won the 2022 FIFA World Cup final against France on penalties.",
    "Qatar hosted the 2022 FIFA World Cup.",
    "Lionel Messi scored twice in the 2022 World Cup final.",
]

ids = ["chunk-1", "chunk-2", "chunk-3"]
embeddings = [client.embed(text) for text in texts]
metadatas = [
    {"document_id": "doc-1", "team_a": "Argentina", "team_b": "France", "year": 2022},
    {"document_id": "doc-2", "team_a": "Qatar", "year": 2022},
    {"document_id": "doc-3", "player": "Lionel Messi", "year": 2022},
]

repo.upsert(
    ids=ids,
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
)

query = "Who won the 2022 World Cup final?"
query_embedding = client.embed(query)
results = repo.search(query_embedding, top_k=3)

print(f"Query: {query}")
print(f"Results: {len(results)}")
print()

for result in results:
    print(f"score={result.score:.4f}")
    print(f"chunk_id={result.chunk_id}")
    print(f"document_id={result.document_id}")
    print(result.content)
    print()
