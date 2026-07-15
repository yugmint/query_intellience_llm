# src/retrieval/memory.py

from langchain_core.chat_history import InMemoryChatMessageHistory
from src.utils.logger import logger

def get_memory():
    logger.debug("Initializing in-memory chat history.")
    return InMemoryChatMessageHistory()