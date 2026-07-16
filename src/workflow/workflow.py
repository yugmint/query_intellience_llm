from langgraph.graph import START, END, StateGraph

from src.workflow.state import RAGState
from src.workflow.resources import RAGResources

from src.workflow.nodes.intent import detect_intent
from src.workflow.nodes.retrieve_context import retrieve_documents
from src.workflow.nodes.generate_knowledge import generate_knowledge_response
from src.workflow.nodes.generate_conversation import generate_conversation
from src.workflow.nodes.update_memory import update_memory
from src.workflow.nodes.input_guardrail import validate_input
from src.workflow.nodes.guardrail_response import guardrail_response
from src.workflow.nodes.process_query import process_query

def route_guardrail(state):

    if state["is_valid"]:
        return "continue"

    return "reject"

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
    "input_guardrail",
    lambda state: validate_input(
            state,
            resources,
        ),
    )
    
    builder.add_node(
    "guardrail_response",
    lambda state: guardrail_response(
            state,
            resources,
        ),
    )

    builder.add_node(
        "process_query",
        lambda state: process_query(
            state, 
            resources
        ),
    )

    builder.add_node(
        "intent",
        lambda state: detect_intent(
            state, 
            resources
        ),
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

    builder.add_edge(
    START,
        "input_guardrail",
    )

    builder.add_conditional_edges(
    "input_guardrail",
    route_guardrail,
        {
            "continue": "intent",
            "reject": "guardrail_response",
        },
    )

    builder.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "knowledge": "process_query",
            "conversation": "conversation",
        },
    )

    # Knowledge Branch
    builder.add_edge(
        "process_query", 
        "retrieve"
        )
    
    builder.add_edge(
        "retrieve", 
        "generate"
        )
    
    builder.add_edge(
        "generate", 
        "memory")

    # Conversation Branch
    builder.add_edge(
        "conversation", 
        "memory"
        )

    # Memory Branch
    builder.add_edge(
        "memory", 
        END
        )

    #End
    builder.add_edge(
    "guardrail_response",
    END,
        )

    return builder.compile()