from dataclasses import dataclass
from typing import Any

from src.retrieval.embeddings import EmbeddingFactory
from src.retrieval.llm import LLMFactory
from src.retrieval.reranker import RerankerFactory
from src.retrieval.retriever import RetrieverFactory
from src.retrieval.vectorstore import VectorStoreFactory


@dataclass(slots=True)
class RAGResources:
    """
    Shared application resources.

    Deliberately does NOT hold conversation memory -- memory is
    per-session, not a process-wide singleton like the llm/embeddings/
    vectorstore/retriever/reranker are. Each request carries its own
    session's memory object through `RAGState["session_memory"]` instead
    (see RAGService.ask()). Mutating a resource here as a stand-in for
    "current session" would race under concurrent requests for
    different sessions.
    """

    llm: Any
    embeddings: Any
    vectorstore: Any
    retriever: Any
    reranker: Any


def build_resources() -> RAGResources:
    """
    Build all shared resources once.
    """

    # Build once
    embeddings = EmbeddingFactory.get()

    # Reuse the same embedding instance
    vectorstore = VectorStoreFactory.load(embeddings)

    retriever = RetrieverFactory.build(vectorstore)

    reranker = RerankerFactory.get()

    llm = LLMFactory.get()

    return RAGResources(
        llm=llm,
        embeddings=embeddings,
        vectorstore=vectorstore,
        retriever=retriever,
        reranker=reranker,
    )