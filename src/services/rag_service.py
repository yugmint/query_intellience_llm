from langchain_core.chat_history import InMemoryChatMessageHistory

from src.retrieval.memory import get_memory
from src.retrieval.retriever import RetrieverFactory
from src.retrieval.vectorstore import VectorStoreFactory
from src.utils.chat_history import format_chat_history

from src.workflow.resources import build_resources
from src.workflow.workflow import build_workflow

from src.utils.logger import logger

DEFAULT_SESSION_ID = "default"


class RAGService:
    """
    Public interface for interacting with the RAG system.

    Conversation memory is scoped per `session_id` -- each session gets
    its own InMemoryChatMessageHistory, created on first use. Callers that
    don't care about multi-session isolation (the CLI in main.py) can omit
    session_id entirely and get one implicit shared session, same as
    before.

    Note: this in-memory session store is per-process and non-persistent
    (lost on restart) and has no eviction -- fine for dev/demo traffic,
    not yet a real answer for long-running multi-user production use. See
    docs/05-roadmap.md.
    """

    def __init__(self):

        logger.info("=" * 100)
        logger.info("Initializing RAG Service...")

        # session_id -> InMemoryChatMessageHistory, created lazily
        self._sessions: dict[str, InMemoryChatMessageHistory] = {}

        # Initialize shared resources (llm/embeddings/vectorstore/retriever --
        # NOT memory, which is per-session, see workflow/resources.py)
        self.resources = build_resources()

        # Build LangGraph workflow
        self.workflow = build_workflow(self.resources)

        logger.info("RAG Service initialized successfully.")
        logger.info("=" * 100)

    def _get_session_memory(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self._sessions:
            logger.debug(f"Creating new conversation memory for session '{session_id}'.")
            self._sessions[session_id] = get_memory()

        return self._sessions[session_id]

    def ask(
        self,
        query: str,
        session_id: str = DEFAULT_SESSION_ID,
        return_state: bool = False,
    ):
        """
        Ask a question to the RAG system.

        Parameters
        ----------
        query : str
            User query.

        session_id : str
            Which conversation this query belongs to. Queries with
            different session_ids never see each other's history.

        return_state : bool
            If True, returns the complete workflow state.
            Otherwise returns only the generated answer.

        Returns
        -------
        str | dict
        """

        logger.info("")
        logger.info("=" * 100)
        logger.info(f"New Query [session={session_id}] : {query}")

        memory = self._get_session_memory(session_id)
        chat_history = format_chat_history(memory.messages)

        initial_state = {

            "query": query,

            "intent": "",

            "rewritten_query": "",

            "documents": [],

            "context": "",

            "chat_history": chat_history,

            "session_id": session_id,

            "session_memory": memory,

            "answer": "",

            "retry_count": 0,

            "metadata": {},
        }

        result = self.workflow.invoke(initial_state)

        logger.info("Workflow execution completed.")

        if return_state:
            return result

        return result["answer"]

    def reset_memory(self, session_id: str = DEFAULT_SESSION_ID):
        """
        Clears conversation history for one session (default: the
        implicit shared session used when no session_id is passed).
        """

        logger.info(f"Resetting conversation memory for session '{session_id}'.")

        self._sessions[session_id] = get_memory()

        logger.info("Conversation memory cleared.")

    def reload_index(self):
        """
        Reload the FAISS vectorstore from disk in place.

        The compiled LangGraph workflow closes over `self.resources` by
        reference, not by value, so mutating its `vectorstore` / `retriever`
        fields here is picked up immediately by every node -- no need to
        rebuild the graph. This is what lets a separate ingestion service
        (writing to the same shared index path) hand off a freshly built
        index without restarting this process.
        """

        logger.info("Reloading vector index from disk...")

        self.resources.vectorstore = VectorStoreFactory.load(self.resources.embeddings)
        self.resources.retriever = RetrieverFactory.build(self.resources.vectorstore)

        logger.info("Vector index reloaded.")
