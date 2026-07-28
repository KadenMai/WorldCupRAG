from app.models.search_result import SearchResult


class PromptBuilder:
    def build(self, question: str, results: list[SearchResult]) -> str:
        context = "\n\n".join(result.content for result in results)

        return f"""You are a football assistant.

Answer ONLY using the provided context.

If the answer cannot be found in the context,
say you don't know.

Context:
-----------------------
{context}
-----------------------

Question:
{question}

Answer:
"""
