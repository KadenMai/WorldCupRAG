from app.llm.embedding_client import EmbeddingClient


client = EmbeddingClient()

vector = client.embed("Argentina won the 2022 FIFA World Cup.")

print(len(vector))
print(vector[:10])
