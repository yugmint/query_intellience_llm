from src.workflow.state import RAGState
from src.workflow.resources import RAGResources


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