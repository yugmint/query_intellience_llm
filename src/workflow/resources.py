from dataclasses import dataclass
from typing import Any

from src.retrieval.embeddings import EmbeddingFactory
from src.retrieval.llm import LLMFactory
from src.retrieval.retriever import RetrieverFactory
from src.retrieval.vectorstore import VectorStoreFactory


@dataclass(slots=True)
class RAGResources:
    """
    Shared application resources.

    These objects are created once during application startup
    and reused across the entire workflow.
    """

    llm: Any
    embeddings: Any
    vectorstore: Any
    retriever: Any
    memory: Any


def build_resources(memory) -> RAGResources:
    """
    Initialize and return all shared resources.
    """

    embeddings = EmbeddingFactory.build()

    vectorstore = VectorStoreFactory.load()

    retriever = RetrieverFactory.build(vectorstore)

    llm = LLMFactory.build()

    return RAGResources(
        llm=llm,
        embeddings=embeddings,
        vectorstore=vectorstore,
        retriever=retriever,
        memory=memory,
    )