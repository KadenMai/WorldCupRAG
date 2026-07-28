from app.models.chunk import Chunk
from app.models.document import Document


class Chunker:
    def chunk(self, documents: list[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []

        for document in documents:
            chunks.append(
                Chunk(
                    id=f"{document.id}-chunk-1",
                    document_id=document.id,
                    content=document.content,
                    metadata=document.metadata,
                )
            )

        return chunks
