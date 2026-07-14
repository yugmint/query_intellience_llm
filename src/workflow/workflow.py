from langgraph.graph import START, END, StateGraph

from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.workflow.nodes.intent import detect_intent
from src.workflow.nodes.retrieve_context import retrieve_documents
from src.workflow.nodes.generate_knowledge import generate_knowledge_response
from src.workflow.nodes.generate_conversation import generate_conversation
from src.workflow.nodes.update_memory import update_memory


def route_by_intent(state: RAGState) -> str:
    """
    Route execution based on detected intent.
    """

    intent = state.get("intent", "knowledge")

    if intent == "knowledge":
        return "knowledge"

    return "conversation"


def build_workflow(resources: RAGResources):
    """
    Build and compile the LangGraph workflow.
    """

    builder = StateGraph(RAGState)

    # -------------------------
    # Register Nodes
    # -------------------------

    builder.add_node(
        "intent",
        lambda state: detect_intent(state, resources),
    )

    builder.add_node(
        "retrieve",
        lambda state: retrieve_documents(state, resources),
    )

    builder.add_node(
        "generate",
        lambda state: generate_knowledge_response(state, resources),
    )

    builder.add_node(
        "conversation",
        lambda state: generate_conversation(state, resources),
    )

    builder.add_node(
        "memory",
        lambda state: update_memory(state, resources),
    )

    # -------------------------
    # Workflow
    # -------------------------

    builder.add_edge(START, "intent")

    builder.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "knowledge": "retrieve",
            "conversation": "conversation",
        },
    )

    # Knowledge Branch
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", "memory")

    # Conversation Branch
    builder.add_edge("conversation", "memory")

    # End
    builder.add_edge("memory", END)

    return builder.compile()