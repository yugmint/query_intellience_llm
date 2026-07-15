from src.guardrails.input_guardrail import InputGuardrail

from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.utils.decorators import log_node

@log_node("Input Guardrail")
def validate_input(
    state: RAGState,
    resources: RAGResources,
):
    guardrail = InputGuardrail()

    return guardrail.validate(state)