"""
Tests for nodes/process_query.py::process_query, which delegates to the
QueryRewriter singleton (src/processing/query_rewriter.py). The autouse
_reset_query_rewriter_singleton fixture in conftest.py makes sure each
test gets a fresh QueryRewriter bound to that test's FakeLLM.
"""

from tests.conftest import FakeLLM, make_resources

from src.workflow.nodes.process_query import process_query


def test_no_chat_history_skips_the_llm_entirely():
    llm = FakeLLM("should never be used")
    state = {"query": "What did she say?", "chat_history": ""}

    result = process_query(state, make_resources(llm=llm))

    assert result["rewritten_query"] == "What did she say?"
    assert llm.call_count == 0


def test_no_pronoun_reference_skips_the_llm():
    llm = FakeLLM("should never be used")
    state = {"query": "Explain Kubernetes networking.", "chat_history": "user: hi\nassistant: hello"}

    result = process_query(state, make_resources(llm=llm))

    assert result["rewritten_query"] == "Explain Kubernetes networking."
    assert llm.call_count == 0


def test_pronoun_with_history_triggers_rewrite():
    llm = FakeLLM('{"rewritten_query": "author of the Deep Learning book"}')
    state = {
        "query": "who wrote it?",
        "chat_history": 'user: tell me about "Deep Learning"\nassistant: it is a textbook',
    }

    result = process_query(state, make_resources(llm=llm))

    assert result["rewritten_query"] == "author of the Deep Learning book"
    assert llm.call_count == 1


def test_malformed_rewrite_response_falls_back_to_original_query():
    llm = FakeLLM("not JSON at all")
    state = {"query": "what about that one?", "chat_history": "user: hi\nassistant: hello"}

    result = process_query(state, make_resources(llm=llm))

    assert result["rewritten_query"] == "what about that one?"


def test_empty_rewritten_query_falls_back_to_original():
    llm = FakeLLM('{"rewritten_query": "   "}')
    state = {"query": "what about that one?", "chat_history": "user: hi\nassistant: hello"}

    result = process_query(state, make_resources(llm=llm))

    assert result["rewritten_query"] == "what about that one?"


def test_metadata_records_original_and_rewritten_query():
    llm = FakeLLM('{"rewritten_query": "resolved query"}')
    state = {"query": "what about it?", "chat_history": "user: hi\nassistant: hello"}

    result = process_query(state, make_resources(llm=llm))

    assert result["metadata"]["query_processing"]["original_query"] == "what about it?"
    assert result["metadata"]["query_processing"]["rewritten_query"] == "resolved query"
