from dataclasses import dataclass

from src.retrieval.llm import get_llm
from src.retrieval.embeddings import get_embeddings
from src.retrieval.vectorstore import load_vectorstore
from src.retrieval.retriever import get_retriever


@dataclass
class RAGResources:

    llm: object
    embeddings: object
    vectorstore: object
    retriever: object
    memory: object


def build_resources(memory):

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