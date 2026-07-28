from ollama import Client

class OllamaClient:
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "qwen2.5:1.5b",
    ):
        self.client = Client(host=host)
        self.model = model

    def chat(self, messages: list[dict]) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": messages
                }
            ]
        )

        return response["message"]["content"]