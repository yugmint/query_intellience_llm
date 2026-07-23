"""
Tests for nodes/guardrail_response.py::guardrail_response.
"""

from src.workflow.nodes.guardrail_response import guardrail_response


def test_uses_guardrail_reason_as_the_answer():
    state = {"guardrail_reason": "LengthValidator: query exceeds 512 characters."}

    result = guardrail_response(state, resources=None)

    assert result["answer"] == "LengthValidator: query exceeds 512 characters."
    assert result["status"] == "rejected"
    assert result["metadata"]["guardrail"]["passed"] is False
    assert result["metadata"]["guardrail"]["reason"] == state["guardrail_reason"]


def test_defaults_to_generic_message_when_reason_missing():
    result = guardrail_response({}, resources=None)

    assert result["answer"] == "Invalid request."


def test_existing_metadata_is_preserved():
    state = {"guardrail_reason": "blocked", "metadata": {"session_id": "abc"}}

    result = guardrail_response(state, resources=None)

    assert result["metadata"]["session_id"] == "abc"
    assert result["metadata"]["guardrail"]["reason"] == "blocked"
