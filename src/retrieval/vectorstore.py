# src/retrieval/vectorstore.py

from langchain_community.vectorstores import FAISS

from src.retrieval.config import FAISS_PATH


class VectorStoreFactory:
    """Factory for FAISS vector store."""

    @staticmethod
    def load(embeddings):

        return FAISS.load_local(
            FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )


def load_vectorstore(embeddings):
    return VectorStoreFactory.load(embeddings)