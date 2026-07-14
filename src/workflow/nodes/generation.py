import json

from src.workflow.resources import RAGResources
from src.workflow.state import RAGState

from src.prompts.generation import build_generation_prompt


def generate_answer(
    state: RAGState,
    resources: RAGResources,
):

    prompt = build_generation_prompt(
        query=state["query"],
        context=state["context"],
        chat_history=state["chat_history"],
    )

    response = resources.llm.invoke(prompt)

    content = response.content

    try:

        cleaned = (
            content.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(cleaned)

        answer = parsed.get("response", content)

    except Exception:

        answer = content

    return {
        "answer": answer
    }