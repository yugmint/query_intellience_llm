# src/ingestion/embedders/embedder.py

from src.retrieval.embeddings import (
    EmbeddingFactory,
)


class Embedder:

    """
    Wrapper around the application's
    embedding model.
    """

    @staticmethod
    def get():

        return EmbeddingFactory.get()