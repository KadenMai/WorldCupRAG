from app.llm.ollama_client import OllamaClient


def main():
    llm = OllamaClient()

    answer = llm.chat("Say Hello in one sentence")

    print(answer)


if __name__ == "__main__":
    main()
