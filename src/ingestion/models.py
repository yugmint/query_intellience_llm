# src/ingestion/models.py

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DocumentChunk:
    """
    Represents a processed chunk ready for embedding.
    """

    chunk_id: int

    text: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(slots=True)
class EmbeddingRecord:
    """
    Represents an embedded chunk.
    """

    chunk: DocumentChunk

    embedding_dimension: int


@dataclass(slots=True)
class IngestionReport:
    """
    Summary of an ingestion run.
    """

    source: str

    total_pages: int

    total_chunks: int

    average_chunk_size: float

    embedding_model: str

    vector_store: str

    processing_time: float