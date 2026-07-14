import os
import json
from langchain.chat_models import init_chat_model
from src.retrieval.config import MODEL_NAME


class LLMFactory:
    """Factory for LLM client instances."""

    @staticmethod
    def _load_api_key():
        with open("cred.json") as f:
            data = json.load(f)
            os.environ["GROQ_API_KEY"] = data["grok_api_key"]

    @classmethod
    def build(cls):
        cls._load_api_key()
        return init_chat_model(MODEL_NAME, model_provider="groq")


def get_llm():
    return LLMFactory.build()