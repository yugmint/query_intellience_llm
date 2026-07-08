from typing import TypedDict
from langchain_core.documents import Document


class RAGState(TypedDict):
    """
    Shared state passed between LangGraph nodes.
    """

    # User Input
    query: str

    # Intent
    intent: str

    # Retrieval
    rewritten_query: str
    retrieved_docs: list[Document]
    context: str

    # Conversation
    chat_history: str

    # Final Output
    answer: str

    # Workflow Metadata
    retry_count: int
    metadata: dict