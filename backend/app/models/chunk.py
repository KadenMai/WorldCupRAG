from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    content: str
    metadata: dict[str, object]