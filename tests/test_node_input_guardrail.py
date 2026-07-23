"""
Tests for nodes/input_guardrail.py::validate_input -- a thin wrapper
around InputGuardrail (already covered in depth by
tests/test_guardrail_validators.py and tests/test_input_guardrail.py).
This just confirms the node wiring itself works.
"""

from src.workflow.nodes.input_guardrail import validate_input


def test_valid_query_passes_through():
    state = {"query": "a normal question"}

    result = validate_input(state, resources=None)

    assert result["is_valid"] is True


def test_invalid_query_is_rejected():
    state = {"query": "   "}

    result = validate_input(state, resources=None)

    assert result["is_valid"] is False
    assert "EmptyQueryValidator" in result["guardrail_reason"]
