from langchain_huggingface import HuggingFaceEmbeddings
from src.retrieval.config import EMBEDDING_MODEL


class EmbeddingFactory:
    """Factory for embedding model instances."""

    @staticmethod
    def build():
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_embeddings():
    return EmbeddingFactory.build()