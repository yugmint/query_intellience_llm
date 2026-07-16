from langchain_core.documents import Document

from src.ingestion.chunkers.base import BaseChunker
from src.ingestion.config import IngestionConfig
from src.utils.logger import logger


class RecursiveChunker(BaseChunker):

    def __init__(self, config: IngestionConfig):
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap
        self.separators = list(config.separators)

    def chunk(self, documents: list[Document]) -> list[Document]:
        logger.info("Recursive Chunking...")

        chunks: list[Document] = []

        for document in documents:
            text = document.page_content or ""
            if not text:
                continue

            parts = self._split_text(text)
            for part in parts:
                chunks.append(
                    Document(
                        page_content=part,
                        metadata={**document.metadata},
                    )
                )

        logger.info(f"Chunks Created : {len(chunks)}")
        return chunks

    def _split_text(self, text: str) -> list[str]:
        if not text:
            return []

        separator = self._pick_separator(text)
        parts = text.split(separator)
        return [part.strip() for part in parts if part.strip()]

    def _pick_separator(self, text: str) -> str:
        for separator in self.separators:
            if separator and separator in text:
                return separator
        return "\n"
