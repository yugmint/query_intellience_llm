def build_generation_prompt(
    *,
    query: str,
    context: str,
    chat_history: str,
) -> str:
    """
    Build the prompt for answer generation.
    """

    return f"""
You are an intelligent AI assistant.

Your task is to answer the user's question using ONLY the provided context.

Guidelines:
- Use the provided context whenever possible.
- If the answer is not present in the context, reply with:
  "I don't know."
- Do not make up facts.
- Be concise and accurate.
- Never mention that you were given context.
- Never expose your reasoning process.

--------------------------
Conversation History
--------------------------
{chat_history}

--------------------------
Context
--------------------------
{context}

--------------------------
User Question
--------------------------
{query}
"""