# src/workflow/state.py

from typing import Any, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    """
    Shared state passed between LangGraph nodes.
    """

    # -------------------------
    # User Input
    # -------------------------
    query: str
    rewritten_query: str

    # -------------------------
    # Guardrails
    # -------------------------
    is_valid: bool
    guardrail_reason: str | None

    # -------------------------
    # Intent
    # -------------------------
    intent: str

    # -------------------------
    # Retrieval
    # -------------------------
    retrieved_documents: list[Document]
    reranked_documents: list[Document]
    context: str

    # -------------------------
    # Conversation
    # -------------------------
    chat_history: str

    # -------------------------
    # Generation
    # -------------------------
    answer: str

    # -------------------------
    # Workflow
    # -------------------------
    retry_count: int
    status: str

    # -------------------------
    # Observability
    # -------------------------
    metadata: dict[str, Any]