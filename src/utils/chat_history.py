from langchain_core.messages import BaseMessage

def format_chat_history(messages) -> str:
    """
    Convert LangChain messages into formatted conversation.
    """
    history = []

    for message in messages:

        role = "user" if message.type == "human" else "assistant"

        history.append(
            f"{role}: {message.content}"
        )

    return "\n".join(history)