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
    """

    llm: Any
    embeddings: Any
    vectorstore: Any
    retriever: Any
    memory: Any


def build_resources(memory) -> RAGResources:
    """
    Build all shared resources once.
    """

    # Build once
    embeddings = EmbeddingFactory.get()

    # Reuse the same embedding instance
    vectorstore = VectorStoreFactory.load(embeddings)

    retriever = RetrieverFactory.build(vectorstore)

    llm = LLMFactory.get()

    return RAGResources(
        llm=llm,
        embeddings=embeddings,
        vectorstore=vectorstore,
        retriever=retriever,
        memory=memory,
    )