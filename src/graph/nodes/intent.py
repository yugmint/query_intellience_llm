from src.graph.state import RAGState
from src.graph.resources import RAGResources

import json


def detect_intent(
    state: RAGState,
    resources: RAGResources,
):

    chat_history = state.get("chat_history", "")

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
{state["query"]}
"""

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

        intent = "knowledge"

    return {
        "intent": intent
    }