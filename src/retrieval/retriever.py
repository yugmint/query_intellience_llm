# src/retrieval/retriever.py

from src.retrieval.config import TOP_K


class RetrieverFactory:
    """Factory for retriever instances."""

    @staticmethod
    def build(vectorstore):
        return vectorstore.as_retriever(search_kwargs={"k": TOP_K})


def get_retriever(vectorstore):
    return RetrieverFactory.build(vectorstore)