from typing import Any, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    """
    Shared state passed between LangGraph nodes.
    """

    # User Query
    query: str

    # Intent Classification
    intent: str

    # Query Processing
    rewritten_query: str

    # Retrieved Knowledge
    documents: list[Document]
    context: str

    # Conversation
    chat_history: str

    # Final Response
    answer: str

    # Workflow
    retry_count: int
    status: str

    # Debug / Observability
    metadata: dict[str, Any]