from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Guardrail_Response")
def guardrail_response(
    state: RAGState,
    resources: RAGResources,
):
    """
    Handles invalid user input blocked by the Input Guardrail.
    """

    reason = state.get(
        "guardrail_reason",
        "Invalid request."
    )

    logger.warning(
        f"Request rejected by guardrail: {reason}"
    )

    return {
        "answer": reason,
        "status": "rejected",
        "metadata": {
            **state.get("metadata", {}),
            "guardrail": {
                "passed": False,
                "reason": reason,
            },
        },
    }