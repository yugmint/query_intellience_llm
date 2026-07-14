from src.workflow.resources import RAGResources
from src.workflow.state import RAGState

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Memory")
def update_memory(
    state: RAGState,
    resources: RAGResources,
):

    # ------------------------
    # Prepare
    # ------------------------

    query = state["query"]
    answer = state["answer"]

    # ------------------------
    # Execute
    # ------------------------

    resources.memory.add_user_message(query)
    resources.memory.add_ai_message(answer)

    # ------------------------
    # Metrics
    # ------------------------

    logger.info(
        f"Conversation Length : {len(resources.memory.messages)} messages"
    )

    # ------------------------
    # Return
    # ------------------------

    return {
        "metadata": {
            **state.get("metadata", {}),
            "conversation_length": len(resources.memory.messages),
        },
    }