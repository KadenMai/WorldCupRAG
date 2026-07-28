from app.llm.ollama_client import OllamaClient


def main():
    llm = OllamaClient()

    answer = llm.chat("Say Hello in one sentence")

    worldcup_answer = llm.ask_about_worldcup()

    print(answer)
    print(worldcup_answer)

if __name__ == "__main__":
    main()
