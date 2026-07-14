import json

from src.prompts.generation import build_generation_prompt

from src.workflow.resources import RAGResources
from src.workflow.state import RAGState

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Generation")
def generate_answer(
    state: RAGState,
    resources: RAGResources,
):

    # ------------------------
    # Prepare
    # ------------------------

    logger.info("Building generation prompt.")

    prompt = build_generation_prompt(
        query=state["query"],
        context=state["context"],
        chat_history=state["chat_history"],
    )

    # ------------------------
    # Execute
    # ------------------------

    logger.info("Invoking LLM.")

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

        logger.warning("Structured JSON response not received.")

        answer = content

    # ------------------------
    # Metrics
    # ------------------------

    logger.info(f"Generated Answer Length : {len(answer)}")

    # ------------------------
    # Return
    # ------------------------

    return {
        "answer": answer,
        "metadata": {
            **state.get("metadata", {}),
            "response_length": len(answer),
        },
    }