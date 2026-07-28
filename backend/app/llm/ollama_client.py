from ollama import Client


class OllamaClient:
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "qwen2.5:1.5b",
    ):
        self.client = Client(host=host)
        self.model = model

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
