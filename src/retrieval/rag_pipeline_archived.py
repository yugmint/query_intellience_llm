from src.retrieval.embeddings import get_embeddings
from src.retrieval.llm import get_llm
from src.retrieval.vectorstore import load_vectorstore
from src.retrieval.retriever import get_retriever

import json


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
                f"User: {msg.content}"
                if msg.type == "human"
                else f"Assistant: {msg.content}"
                for msg in self.memory.messages
            ]
        )

    def query(self, user_query):

        # Retrieve documents
        docs = self.retriever.invoke(user_query)

        context = (
            "\n\n".join([doc.page_content for doc in docs])
            if docs
            else ""
        )

        # Optional: limit context size
        context = context[:3000]

        chat_history = self.format_chat_history()

        prompt = f"""
You are an intelligent assistant.

Your task:
1. Detect the intent
2. Generate the final response

Intent categories:
- greeting
- chit_chat
- knowledge

IMPORTANT:
Return ONLY valid JSON.

Format:
{{
    "intent": "greeting | chit_chat | knowledge",
    "response": "final response here"
}}

Rules:
- If greeting → respond casually
- If chit_chat → respond naturally
- If knowledge → answer ONLY from context
- If answer not in context → say "I don't know"
- Never include raw context
- Never explain reasoning
- Never output anything except JSON

--- Chat History ---
{chat_history}

--- Context ---
{context}

--- User Question ---
{user_query}
"""

        try:
            response = self.llm.invoke(prompt)

            # Clean markdown formatting if model returns ```json
            cleaned_response = (
                response.content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            parsed = json.loads(cleaned_response)

            final_response = parsed.get(
                "response",
                "Something went wrong."
            )

        except Exception as e:
            print(f"[ERROR]: {e}")
            final_response = "Something went wrong."

        # Save memory
        self.memory.add_user_message(user_query)
        self.memory.add_ai_message(final_response)

        return final_response