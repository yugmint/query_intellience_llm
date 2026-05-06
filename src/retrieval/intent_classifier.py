from src.llm import get_llm

def classify_intent(query: str) -> str:
    llm = get_llm()

    prompt = f"""
Classify the user query into one of the following categories:

1. greeting → greetings like hi, hello
2. chit_chat → casual conversation, thanks, jokes, etc.
3. knowledge → questions requiring factual answers from documents

Return ONLY one word: greeting, chit_chat, or knowledge.

Query: {query}
"""

    response = llm.invoke(prompt)

    intent = response.content.strip().lower()

    return intent