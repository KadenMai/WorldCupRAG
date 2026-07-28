import os

from dotenv import load_dotenv
from ollama import Client

load_dotenv()


class OllamaClient:
    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
    ):
        self.client = Client(
            host=host or os.getenv(
                "OLLAMA_HOST",
                "http://localhost:11434",
            )
        )

        self.model = model or os.getenv(
            "OLLAMA_CHAT_MODEL",
            "qwen2.5:1.5b",
        )

    def chat(self, message: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        return response["message"]["content"]

    def ask_about_worldcup(self) -> str:
        return self.chat("Who won the 2022 FIFA World Cup?")