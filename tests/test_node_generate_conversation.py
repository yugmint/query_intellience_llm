"""
Tests for nodes/generate_conversation.py::generate_conversation.
"""

from tests.conftest import FakeLLM, make_resources

from src.workflow.nodes.generate_conversation import generate_conversation


def _state(**overrides):
    state = {"query": "hi there", "intent": "greeting", "chat_history": ""}
    state.update(overrides)
    return state


def test_valid_json_response_extracts_answer():
    llm = FakeLLM('{"response": "Hello! How can I help?"}')

    result = generate_conversation(_state(), make_resources(llm=llm))

    assert result["answer"] == "Hello! How can I help?"
    assert result["metadata"]["intent"] == "greeting"


def test_non_json_response_falls_back_to_raw_content():
    llm = FakeLLM("Hey! Just chatting.")

    result = generate_conversation(_state(), make_resources(llm=llm))

    assert result["answer"] == "Hey! Just chatting."


def test_fallback_on_parse_failure_uses_uncleaned_raw_content():
    """
    Documents a real asymmetry in the node: on the happy path it parses
    `content` (fences stripped), but the except branch falls back to
    `response.content` (the ORIGINAL, un-stripped value) rather than the
    cleaned `content` variable. If the raw response has markdown fences
    around invalid JSON, the fences survive into the answer.
    """
    raw = "```json\nnot actually valid json\n```"
    llm = FakeLLM(raw)

    result = generate_conversation(_state(), make_resources(llm=llm))

    assert result["answer"] == raw


def test_prompt_includes_intent_history_and_query():
    llm = FakeLLM('{"response": "ok"}')
    state = _state(intent="chit_chat", chat_history="user: hi\nassistant: hey", query="what's up")

    generate_conversation(state, make_resources(llm=llm))

    prompt = llm.prompts[0]
    assert "chit_chat" in prompt
    assert "user: hi" in prompt
    assert "what's up" in prompt
