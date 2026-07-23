"""
Tests for nodes/intent.py::detect_intent.
"""

from tests.conftest import FakeLLM, make_resources

from src.workflow.nodes.intent import detect_intent


def test_valid_json_response_is_parsed():
    llm = FakeLLM('{"intent": "greeting"}')
    state = {"query": "hi there", "chat_history": ""}

    result = detect_intent(state, make_resources(llm=llm))

    assert result["intent"] == "greeting"
    assert result["metadata"]["intent"] == "greeting"


def test_markdown_fenced_json_is_stripped_before_parsing():
    llm = FakeLLM('```json\n{"intent": "chit_chat"}\n```')
    state = {"query": "how's it going", "chat_history": ""}

    result = detect_intent(state, make_resources(llm=llm))

    assert result["intent"] == "chit_chat"


def test_malformed_response_falls_back_to_knowledge():
    llm = FakeLLM("not valid json at all")
    state = {"query": "what is the capital of France?", "chat_history": ""}

    result = detect_intent(state, make_resources(llm=llm))

    assert result["intent"] == "knowledge"


def test_missing_intent_key_falls_back_to_knowledge():
    # Valid JSON, but not shaped as expected -- KeyError inside the node
    # should be caught the same way as a JSON parse failure.
    llm = FakeLLM('{"something_else": "greeting"}')
    state = {"query": "hey", "chat_history": ""}

    result = detect_intent(state, make_resources(llm=llm))

    assert result["intent"] == "knowledge"


def test_prompt_includes_query_and_chat_history():
    llm = FakeLLM('{"intent": "knowledge"}')
    state = {"query": "what about the second point?", "chat_history": "user: hi\nassistant: hello"}

    detect_intent(state, make_resources(llm=llm))

    assert "what about the second point?" in llm.prompts[0]
    assert "user: hi" in llm.prompts[0]


def test_existing_metadata_is_preserved():
    llm = FakeLLM('{"intent": "knowledge"}')
    state = {"query": "hi", "chat_history": "", "metadata": {"session_id": "abc"}}

    result = detect_intent(state, make_resources(llm=llm))

    assert result["metadata"]["session_id"] == "abc"
    assert result["metadata"]["intent"] == "knowledge"
