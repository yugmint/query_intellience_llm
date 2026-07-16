# src/ingestion/chunkers/hybrid_chunker.py

from langchain_core.documents import Document

from src.ingestion.chunkers.base import BaseChunker
from src.ingestion.chunkers.recursive_chunker import (
    RecursiveChunker,
)

from src.ingestion.config import IngestionConfig

from src.utils.logger import logger


class HybridChunker(BaseChunker):
    """
    Hybrid chunking strategy.

    Currently delegates to RecursiveChunker.

    Future versions will dynamically choose
    between recursive, semantic and structure-aware
    chunking.
    """

    def __init__(
        self,
        config: IngestionConfig,
    ):

        self.recursive = (
            RecursiveChunker(config)
        )

    def chunk(
        self,
        documents: list[Document],
    ) -> list[Document]:

        logger.info(
            "Hybrid Chunker selected."
        )

        return self.recursive.chunk(
            documents
        )