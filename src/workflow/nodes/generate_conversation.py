import json

from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Generate_Conversation")
def generate_conversation(
    state: RAGState,
    resources: RAGResources,
):

    logger.info(
        f"Conversation Intent : {state['intent']}"
    )

    prompt = f"""
You are a friendly AI assistant.

Respond naturally.

Current intent:
{state["intent"]}

Conversation History:
{state["chat_history"]}

User:
{state["query"]}

Return ONLY JSON.

{{
    "response": "<assistant response>"
}}
"""

    response = resources.llm.invoke(prompt)

    content = (
        response.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        parsed = json.loads(content)

        answer = parsed["response"]

    except Exception:

        answer = response.content

    return {

        "answer": answer,

        "metadata": {

            **state.get("metadata", {}),

            "intent": state["intent"],

        }

    }