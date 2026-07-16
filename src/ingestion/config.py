# src/ingestion/config.py

"""
Global configuration for the ingestion pipeline.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class IngestionConfig:
    """
    Configuration used throughout the ingestion pipeline.
    """

    # -----------------------------
    # Chunking
    # -----------------------------
    chunk_strategy: str = "recursive"

    chunk_size: int = 500

    chunk_overlap: int = 100

    separators: tuple[str, ...] = (
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    )

    # -----------------------------
    # Embeddings
    # -----------------------------
    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    normalize_embeddings: bool = True

    # -----------------------------
    # Indexing
    # -----------------------------
    vector_store: str = "faiss"

    index_path: str = "vectorstore"

    # -----------------------------
    # Metadata
    # -----------------------------
    include_page_number: bool = True

    include_source: bool = True

    include_chunk_id: bool = True

    include_token_count: bool = True

    # -----------------------------
    # Validation
    # -----------------------------
    max_document_size_mb: int = 100

    supported_extensions: tuple[str, ...] = (
        ".pdf",
    )