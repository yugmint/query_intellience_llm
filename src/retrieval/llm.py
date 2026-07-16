# src/retrieval/llm.py

import os
import json
from langchain.chat_models import init_chat_model
from src.retrieval.config import MODEL_NAME
from typing import Optional


class LLMFactory:
    """Factory for LLM client instances."""

    _instance: Optional[any] = None

    @staticmethod
    def _load_api_key():
        with open("cred.json") as f:
            data = json.load(f)
            os.environ["GROQ_API_KEY"] = data["grok_api_key"]

    @classmethod
    def get(cls):

        if cls._instance is None:

            cls._load_api_key()

            cls._instance = init_chat_model(
                MODEL_NAME,
                model_provider="groq",
            )

        return cls._instance

    @classmethod
    def build(cls):
        return cls.get()