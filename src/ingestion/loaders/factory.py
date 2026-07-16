from pathlib import Path

from src.ingestion.loaders.pdf_loader import PDFLoader


class LoaderFactory:
    """
    Returns the appropriate document loader.
    """

    @staticmethod
    def build(file_path: str):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFLoader()

        raise ValueError(
            f"Unsupported document type: {extension}"
        )