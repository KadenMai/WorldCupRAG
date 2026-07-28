from app.ingest.chunker import Chunker
from app.ingest.document_builder import DocumentBuilder
from app.ingest.parser import WorldCupParser
from app.llm.embedding_client import EmbeddingClient
from app.rag.vector_repository import VectorRepository


class Indexer:
    def __init__(
        self,
        parser: WorldCupParser,
        builder: DocumentBuilder,
        chunker: Chunker,
        embedding_client: EmbeddingClient,
        repository: VectorRepository,
    ):
        self.parser = parser
        self.builder = builder
        self.chunker = chunker
        self.embedding_client = embedding_client
        self.repository = repository

    def index(self, folder: str) -> dict[str, int]:
        print("Loading tournament...")
        tournament = self.parser.load(folder)
        print(f"{len(tournament.matches)} matches loaded")

        documents = self.builder.build(tournament)
        print(f"{len(documents)} documents created")

        chunks = self.chunker.chunk(documents)
        print(f"{len(chunks)} chunks created")

        ids = [chunk.id for chunk in chunks]
        contents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                **chunk.metadata,
                "document_id": chunk.document_id,
            }
            for chunk in chunks
        ]

        print("Generating embeddings...")
        embeddings = self.embedding_client.embed_many(contents)

        print("Saving to Chroma...")
        self.repository.upsert(
            ids=ids,
            documents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print("Done.")
        return {
            "year": tournament.year,
            "matches": len(tournament.matches),
            "documents": len(documents),
            "chunks": len(chunks),
        }
