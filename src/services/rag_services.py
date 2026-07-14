from src.retrieval.memory import get_memory

from src.workflow.resources import build_resources
from src.workflow.workflow import build_workflow

from src.utils.logger import logger


class RAGService:
    """
    Public interface for interacting with the RAG system.
    """

    def __init__(self):

        logger.info("=" * 100)
        logger.info("Initializing RAG Service...")

        # Initialize memory
        self.memory = get_memory()

        # Initialize shared resources
        self.resources = build_resources(self.memory)

        # Build LangGraph workflow
        self.workflow = build_workflow(self.resources)

        logger.info("RAG Service initialized successfully.")
        logger.info("=" * 100)

    def ask(
        self,
        query: str,
        return_state: bool = False,
    ):
        """
        Ask a question to the RAG system.

        Parameters
        ----------
        query : str
            User query.

        return_state : bool
            If True, returns the complete workflow state.
            Otherwise returns only the generated answer.

        Returns
        -------
        str | dict
        """

        logger.info("")
        logger.info("=" * 100)
        logger.info(f"New Query : {query}")

        initial_state = {

            "query": query,

            "intent": "",

            "rewritten_query": "",

            "retrieved_docs": [],

            "context": "",

            "chat_history": "",

            "answer": "",

            "retry_count": 0,

            "metadata": {},
        }

        result = self.workflow.invoke(initial_state)

        logger.info("Workflow execution completed.")

        if return_state:
            return result

        return result["answer"]

    def reset_memory(self):
        """
        Clears conversation history.
        """

        logger.info("Resetting conversation memory.")

        self.memory = get_memory()

        self.resources.memory = self.memory

        logger.info("Conversation memory cleared.")