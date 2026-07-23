"""
Tests for nodes/update_memory.py::update_memory.

Uses the real InMemoryChatMessageHistory rather than a fake -- it's a
plain in-process object with no external calls, so there's no reason to
mock it.
"""

from langchain_core.chat_history import InMemoryChatMessageHistory

from src.workflow.nodes.update_memory import update_memory


def test_appends_user_and_ai_messages():
    memory = InMemoryChatMessageHistory()
    state = {
        "query": "what is Ajji's role?",
        "answer": "Ajji is the grandmother.",
        "session_memory": memory,
        "session_id": "s1",
    }

    update_memory(state, resources=None)

    assert len(memory.messages) == 2
    assert memory.messages[0].content == "what is Ajji's role?"
    assert memory.messages[0].type == "human"
    assert memory.messages[1].content == "Ajji is the grandmother."
    assert memory.messages[1].type == "ai"


def test_conversation_length_metadata_reflects_message_count():
    memory = InMemoryChatMessageHistory()
    memory.add_user_message("earlier turn")
    memory.add_ai_message("earlier answer")

    state = {
        "query": "second question",
        "answer": "second answer",
        "session_memory": memory,
        "session_id": "s1",
    }

    result = update_memory(state, resources=None)

    assert result["metadata"]["conversation_length"] == 4


def test_existing_metadata_is_preserved():
    memory = InMemoryChatMessageHistory()
    state = {
        "query": "q",
        "answer": "a",
        "session_memory": memory,
        "session_id": "s1",
        "metadata": {"intent": "knowledge"},
    }

    result = update_memory(state, resources=None)

    assert result["metadata"]["intent"] == "knowledge"
    assert "conversation_length" in result["metadata"]


def test_different_sessions_use_independent_memory_objects():
    memory_a = InMemoryChatMessageHistory()
    memory_b = InMemoryChatMessageHistory()

    update_memory(
        {"query": "a-query", "answer": "a-answer", "session_memory": memory_a, "session_id": "a"},
        resources=None,
    )

    assert len(memory_a.messages) == 2
    assert len(memory_b.messages) == 0
