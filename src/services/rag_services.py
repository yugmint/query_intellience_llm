from src.retrieval.memory import get_memory

from src.workflow.resources import build_resources
from src.workflow.workflow import build_workflow


class RAGService:
    """
    Public interface for interacting with the RAG system.
    """

    def __init__(self):

        # Initialize shared resources once
        self.memory = get_memory()

        self.resources = build_resources(self.memory)

        self.workflow = build_workflow(self.resources)

    def ask(self, query: str) -> str:

        initial_state = {
            "query": query,

            "intent": "",

            "rewritten_query": "",

            "documents": [],

            "context": "",

            "chat_history": "",

            "answer": "",

            "retry_count": 0,

            "status": "success",

            "metadata": {},
        }

        result = self.workflow.invoke(initial_state)

        return result["answer"]

    def reset_memory(self):

        self.memory.clear()