# src/ingestion/indexers/faiss_indexer.py

from langchain_community.vectorstores import FAISS

from src.utils.logger import logger


class FAISSIndexer:

    """
    Builds and persists a FAISS index.
    """

    def build(
        self,
        chunks,
        embeddings,
    ):

        logger.info("=" * 80)
        logger.info("Building FAISS Index")

        vectorstore = FAISS.from_documents(
            chunks,
            embeddings,
        )

        logger.info(
            "FAISS index created."
        )

        return vectorstore

    def save(
        self,
        vectorstore,
        path,
    ):

        logger.info(
            f"Saving index -> {path}"
        )

        vectorstore.save_local(path)