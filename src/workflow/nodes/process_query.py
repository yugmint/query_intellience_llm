from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.processing.query_rewriter import QueryRewriter

from src.utils.decorators import log_node
from src.utils.logger import logger

@log_node("Process Query")
def process_query(
    state: RAGState,
    resources: RAGResources,
):
    """
    Rewrite the user's query to improve document retreival quality.

    if the query is already clear, it will be returned unchanged.
    """

    logger.info(f"Processing Query : {state['query']}")

    rewritter = QueryRewriter.get(resources)

    rewritten_query = rewritter.rewrite(
        query=state["query"],
        chat_history=state.get("chat_history", ""),
    )

    return {
        "rewritten_query": rewritten_query,
        "metadata": {
            **state.get("metadata", {}),
            "query_processing": {
                "query_rewriter": "rewrite_query != state['query']",
                "original_query": state["query"],
                "rewritten_query": rewritten_query,
                },
            },
        }