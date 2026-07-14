from src.workflow.resources import RAGResources
from src.workflow.state import RAGState


def update_memory(
    state: RAGState,
    resources: RAGResources,
):

    # Save conversation

    resources.memory.add_user_message(
        state["query"]
    )

    resources.memory.add_ai_message(
        state["answer"]
    )

    return {}