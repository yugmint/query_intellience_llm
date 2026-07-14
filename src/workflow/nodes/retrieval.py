from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Retrieval")
def retrieve_documents(
    state: RAGState,
    resources: RAGResources,
):

    # ------------------------
    # Prepare
    # ------------------------

    query = state.get("rewritten_query") or state["query"]

    logger.info(f"Retrieval Query : {query}")

    # ------------------------
    # Execute
    # ------------------------

    documents = resources.retriever.invoke(query)

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # ------------------------
    # Business Metrics
    # ------------------------

    logger.info(f"Retrieved Documents : {len(documents)}")
    logger.info(f"Context Length      : {len(context)} chars")

    # Optional (avoid logging huge content)
    logger.debug(f"Context Preview:\n{context[:300]}")

    # ------------------------
    # Return
    # ------------------------

    return {
        "documents": documents,
        "context": context,
    }