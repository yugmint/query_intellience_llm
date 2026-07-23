from src.workflow.resources import RAGResources
from src.workflow.state import RAGState

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Update_Memory")
def update_memory(
    state: RAGState,
    resources: RAGResources,
):

    # ------------------------
    # Prepare
    # ------------------------

    query = state["query"]
    answer = state["answer"]
    memory = state["session_memory"]

    # ------------------------
    # Execute
    # ------------------------

    memory.add_user_message(query)
    memory.add_ai_message(answer)

    # ------------------------
    # Metrics
    # ------------------------

    logger.info(
        f"Conversation Length : {len(memory.messages)} messages "
        f"(session={state.get('session_id', 'default')})"
    )

    # ------------------------
    # Return
    # ------------------------

    return {
        "metadata": {
            **state.get("metadata", {}),
            "conversation_length": len(memory.messages),
        },
    }