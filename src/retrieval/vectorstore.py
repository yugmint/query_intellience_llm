from langchain_community.vectorstores import FAISS
from src.retrieval.embeddings import EmbeddingFactory
from src.retrieval.config import FAISS_PATH


class VectorStoreFactory:
    """Factory for vector store instances."""

    @staticmethod
    def load():
        embeddings = EmbeddingFactory.build()
        return FAISS.load_local(
            FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )


def load_vectorstore():
    return VectorStoreFactory.load()