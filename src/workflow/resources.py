from dataclasses import dataclass
from typing import Any

from src.retrieval.embeddings import get_embeddings
from src.retrieval.llm import get_llm
from src.retrieval.retriever import get_retriever
from src.retrieval.vectorstore import load_vectorstore


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

    embeddings = get_embeddings()

    vectorstore = load_vectorstore()

    retriever = get_retriever(vectorstore)

    llm = get_llm()

    return RAGResources(
        llm=llm,
        embeddings=embeddings,
        vectorstore=vectorstore,
        retriever=retriever,
        memory=memory,
    )