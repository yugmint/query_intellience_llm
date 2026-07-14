from langgraph.graph import START, END, StateGraph

from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.workflow.nodes.intent import detect_intent
from src.workflow.nodes.retrieval import retrieve_documents
from src.workflow.nodes.generation import generate_answer
from src.workflow.nodes.memory import update_memory


def build_workflow(resources: RAGResources):
    """
    Build and compile the LangGraph workflow.
    """

    builder = StateGraph(RAGState)

    # Register Nodes
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
        lambda state: generate_answer(state, resources),
    )

    builder.add_node(
        "memory",
        lambda state: update_memory(state, resources),
    )

    # Define Workflow
    builder.add_edge(START, "intent")
    builder.add_edge("intent", "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", "memory")
    builder.add_edge("memory", END)

    return builder.compile()