import json

from src.workflow.resources import RAGResources
from src.workflow.state import RAGState

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Intent")
def detect_intent(
    state: RAGState,
    resources: RAGResources,
):

    # ------------------------
    # Prepare
    # ------------------------

    query = state["query"]
    chat_history = state.get("chat_history", "")

    logger.info(f"Processing Query : {query}")

    prompt = f"""
You are an intelligent assistant.

Classify the intent of the user's message.

Possible intents:
- greeting
- chit_chat
- knowledge

Return ONLY JSON.

{{
    "intent": "<intent>"
}}

Chat History:
{chat_history}

User:
{query}
"""

    # ------------------------
    # Execute
    # ------------------------

    response = resources.llm.invoke(prompt)

    cleaned = (
        response.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        parsed = json.loads(cleaned)

        intent = parsed["intent"]

    except Exception:

        logger.warning("Intent parsing failed. Falling back to 'knowledge'.")

        intent = "knowledge"

    # ------------------------
    # Metrics
    # ------------------------

    logger.info(f"Detected Intent : {intent}")

    # ------------------------
    # Return
    # ------------------------

    return {
        "intent": intent,
        "metadata": {
            **state.get("metadata", {}),
            "intent": intent,
        },
    }