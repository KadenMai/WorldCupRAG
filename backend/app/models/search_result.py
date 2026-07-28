from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    document_id: str
    chunk_id: str
    content: str
    metadata: dict[str, object]
    score: float
