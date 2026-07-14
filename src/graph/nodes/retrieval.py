from src.graph.state import RAGState
from src.graph.resources import RAGResources


def retrieve_documents(
    state: RAGState,
    resources: RAGResources,
):

    docs = resources.retriever.invoke(
        state["query"]
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return {
        "retrieved_docs": docs,
        "context": context,
    }