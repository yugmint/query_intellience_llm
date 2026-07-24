# src/retrieval/retriever.py

from src.retrieval.config import RERANK_CANDIDATES


class RetrieverFactory:
    """
    Factory for retriever instances.

    Pulls RERANK_CANDIDATES (not TOP_K) from FAISS -- reranking is what
    narrows this down to TOP_K afterward (see nodes/rerank.py). A retriever
    built here that isn't followed by a rerank step will return more
    documents than TOP_K; that's intentional; don't "fix" this back to
    TOP_K without also removing the rerank node from the graph.
    """

    @staticmethod
    def build(vectorstore):
        return vectorstore.as_retriever(search_kwargs={"k": RERANK_CANDIDATES})


def get_retriever(vectorstore):
    return RetrieverFactory.build(vectorstore)