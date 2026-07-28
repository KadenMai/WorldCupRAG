import os

from dotenv import load_dotenv
from ollama import Client


load_dotenv()


class EmbeddingClient:
    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
    ):
        self.client = Client(host=host or os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        self.model = model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    def embed(self, text: str) -> list[float]:
        response = self.client.embed(
            model=self.model,
            input=text,
        )
        return response["embeddings"][0]
