"""
Tests for nodes/retrieve_context.py::retrieve_documents.
"""

from langchain_core.documents import Document

from tests.conftest import FakeRetriever, make_resources

from src.workflow.nodes.retrieve_context import retrieve_documents


def test_uses_rewritten_query_when_present():
    retriever = FakeRetriever([Document(page_content="chunk one")])
    state = {"query": "original query", "rewritten_query": "resolved query", "documents": []}

    retrieve_documents(state, make_resources(retriever=retriever))

    assert retriever.queries == ["resolved query"]


def test_falls_back_to_query_when_rewritten_query_missing():
    retriever = FakeRetriever([Document(page_content="chunk one")])
    state = {"query": "original query", "rewritten_query": "", "documents": []}

    retrieve_documents(state, make_resources(retriever=retriever))

    assert retriever.queries == ["original query"]


def test_context_joins_page_content_with_blank_line():
    docs = [Document(page_content="first chunk"), Document(page_content="second chunk")]
    retriever = FakeRetriever(docs)
    state = {"query": "q", "rewritten_query": "", "documents": []}

    result = retrieve_documents(state, make_resources(retriever=retriever))

    assert result["context"] == "first chunk\n\nsecond chunk"
    assert result["documents"] == docs


def test_no_matches_produces_empty_context():
    retriever = FakeRetriever([])
    state = {"query": "q", "rewritten_query": "", "documents": []}

    result = retrieve_documents(state, make_resources(retriever=retriever))

    assert result["documents"] == []
    assert result["context"] == ""
