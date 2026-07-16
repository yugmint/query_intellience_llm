from pathlib import Path

from langchain_core.documents import Document

from src.utils.logger import logger


class MetadataGenerator:
    """
    Enrich document chunks with metadata.

    This stage prepares chunks for indexing and
    future metadata-aware retrieval.
    """

    def generate(
        self,
        chunks: list[Document],
        source: str,
    ) -> list[Document]:

        logger.info("=" * 80)
        logger.info("Generating Metadata")

        filename = Path(source).name

        for chunk_id, chunk in enumerate(chunks):

            metadata = dict(chunk.metadata)

            metadata.update({

                "chunk_id": chunk_id,

                "source": filename,

                "document_type": Path(source)
                .suffix.lower()
                .replace(".", ""),

                "character_count": len(
                    chunk.page_content
                ),

                "word_count": len(
                    chunk.page_content.split()
                ),

                # Approximation
                "token_estimate": int(
                    len(chunk.page_content) / 4
                ),
            })

            chunk.metadata = metadata

        logger.info(
            f"Metadata generated for {len(chunks)} chunks."
        )

        return chunks