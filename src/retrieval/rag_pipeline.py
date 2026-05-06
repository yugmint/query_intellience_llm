from src.retrieval.llm import get_llm
from src.retrieval.vectorstore import load_vectorstore
from src.retrieval.retriever import get_retriever
from src.retrieval.intent_classifier import classify_intent

class RAGPipeline:
    def __init__(self, memory):
        self.llm = get_llm()
        self.vectorstore = load_vectorstore()
        self.retriever = get_retriever(self.vectorstore)
        self.memory = memory

    def query(self, user_query):
        intent = classify_intent(user_query)

        print(f"[DEBUG] Intent: {intent}")  # optional

        # 🟢 Greeting
        if intent == "greeting":
            return "Hey! How can I assist you today?"

        # 🟡 Chit-chat
        if intent == "chit_chat":
            response = self.llm.invoke(user_query)
            return response.content

        # 🔵 Knowledge → RAG
        docs = self.retriever.invoke(user_query)

        if not docs:
            return "I couldn't find relevant information. Please try rephrasing."

        context = "\n\n".join([doc.page_content for doc in docs])

        chat_history = "\n".join(
            [f"{msg.type}: {msg.content}" for msg in self.memory.messages]
        )

        prompt = f"""
    You are a helpful assistant.

    Use the provided context to answer.
    If answer not in context → say "I don't know"

    --- Chat History ---
    {chat_history}

    --- Context ---
    {context}

    --- Question ---
    {user_query}
    """

        response = self.llm.invoke(prompt)

        self.memory.add_user_message(user_query)
        self.memory.add_ai_message(response.content)

        return response.content