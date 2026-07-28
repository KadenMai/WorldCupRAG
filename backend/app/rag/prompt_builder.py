from app.models.search_result import SearchResult


class PromptBuilder:
    def build(self, question: str, results: list[SearchResult]) -> str:
        context = "\n\n".join(result.content for result in results)

        return f"""You are an expert on the FIFA World Cup.

Answer ONLY using the information contained in the CONTEXT below.

Rules:

1. Use ONLY the context.
2. Never use your own knowledge.
3. If the answer cannot be found in the context, reply:

"I don't know based on the provided documents."

4. Keep the answer concise.

==========================
CONTEXT

{context}

==========================

QUESTION

{question}

==========================

ANSWER
"""
