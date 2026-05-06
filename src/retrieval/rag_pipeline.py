from src.retrieval.embeddings import get_embeddings
from src.retrieval.llm import get_llm
from src.retrieval.vectorstore import load_vectorstore
from src.retrieval.retriever import get_retriever
from src.retrieval.intent_classifier import classify_intent

class RAGPipeline:
    def __init__(self, memory):
        self.llm = get_llm()
        self.memory = memory

        # Load once
        self.embeddings = get_embeddings()
        self.vectorstore = load_vectorstore()
        self.retriever = get_retriever(self.vectorstore)

    def format_chat_history(self):
        return "\n".join(
            [
                f"User: {msg.content}" if msg.type == "human"
                else f"Assistant: {msg.content}"
                for msg in self.memory.messages
            ]
        )

    def query(self, user_query):
        # 🔥 Merge intent + response in ONE LLM call (better design)

        docs = self.retriever.invoke(user_query)
        context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""

        chat_history = self.format_chat_history()

        prompt = f"""
You are an intelligent assistant.

First determine the intent of the user query:
- greeting
- chit_chat
- knowledge

Rules:
- If greeting → respond casually
- If chit_chat → respond naturally
- If knowledge → use the provided context ONLY
- If answer not in context → say "I don't know"

--- Chat History ---
{chat_history}

--- Context ---
{context}

--- Question ---
{user_query}
"""

        response = self.llm.invoke(prompt)

        # Save memory
        self.memory.add_user_message(user_query)
        self.memory.add_ai_message(response.content)

        return response.content