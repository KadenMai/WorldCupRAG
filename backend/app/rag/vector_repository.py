from __future__ import annotations

import json
import os
from pathlib import Path

import chromadb

from app.models.search_result import SearchResult


class VectorRepository:
    def __init__(
        self,
        collection_name: str = "worldcup2022",
        persist_directory: str | Path | None = None,
    ):
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_DIR") or (
                Path(__file__).resolve().parents[2] / "chroma_db"
            )

        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._collection = self.create_collection()

    def create_collection(self):
        return self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, object]],
    ) -> None:
        if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
            raise ValueError("ids, documents, embeddings, and metadatas must have the same length")

        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=[self._sanitize_metadata(metadata) for metadata in metadatas],
        )

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        raw = self._collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = raw.get("ids", [[]])[0]
        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        results: list[SearchResult] = []
        for chunk_id, content, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
            strict=True,
        ):
            metadata = dict(metadata or {})
            document_id = str(metadata.get("document_id", ""))
            results.append(
                SearchResult(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    content=content or "",
                    metadata=metadata,
                    score=1.0 - float(distance),
                )
            )

        return results

    def delete_collection(self) -> None:
        self._client.delete_collection(name=self.collection_name)
        self._collection = self.create_collection()

    def _sanitize_metadata(self, metadata: dict[str, object]) -> dict[str, object]:
        sanitized: dict[str, object] = {}

        for key, value in metadata.items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = json.dumps(value)

        return sanitized
