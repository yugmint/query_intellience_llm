# src/ingestion/loaders/pdf_loader.py

from pathlib import Path

from pypdf import PdfReader
from langchain_core.documents import Document

from src.ingestion.loaders.base import BaseLoader

from src.utils.logger import logger


class PDFLoader(BaseLoader):
    """
    PDF document loader.
    """

    def load(
        self,
        file_path: str,
    ) -> list[Document]:

        logger.info("=" * 80)
        logger.info("Loading PDF Document")

        reader = PdfReader(file_path)

        documents = [
            Document(
                page_content=page.extract_text() or "",
                metadata={
                    "page_number": index + 1,
                    "source": str(Path(file_path).name),
                },
            )
            for index, page in enumerate(reader.pages)
        ]

        logger.info(
            f"Pages Loaded : {len(documents)}"
        )

        return documents