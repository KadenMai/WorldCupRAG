from pathlib import Path

from app.ingest.chunker import Chunker
from app.ingest.document_builder import DocumentBuilder
from app.ingest.indexer import Indexer
from app.ingest.parser import WorldCupParser
from app.llm.embedding_client import EmbeddingClient
from app.rag.vector_repository import VectorRepository


def main() -> None:
    data_folder = Path(__file__).resolve().parents[2] / "data" / "raw" / "2022"

    indexer = Indexer(
        parser=WorldCupParser(str(data_folder)),
        builder=DocumentBuilder(),
        chunker=Chunker(),
        embedding_client=EmbeddingClient(),
        repository=VectorRepository(collection_name="worldcup2022"),
    )

    indexer.index(str(data_folder))


if __name__ == "__main__":
    main()
