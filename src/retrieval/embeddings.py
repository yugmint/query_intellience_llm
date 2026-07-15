# src/retrieval/embeddings.py

import torch

from langchain_huggingface import HuggingFaceEmbeddings

from src.retrieval.config import EMBEDDING_MODEL
from src.utils.logger import logger
from typing import Optional


class EmbeddingFactory:
    """
    Factory for embedding model instances.
    """

    _instance: Optional[HuggingFaceEmbeddings] = None

    @classmethod
    def get(cls):

        if cls._instance is None:

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

            logger.info("=" * 80)
            logger.info("Initializing Embedding Model")
            logger.info(f"Model  : {EMBEDDING_MODEL}")
            logger.info(f"Device : {device.upper()}")

            cls._instance = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={
                    "device": device,
                },
                encode_kwargs={
                    "normalize_embeddings": True,
                },
            )

            logger.info("Embedding model initialized successfully.")

        else:
            logger.debug("Reusing existing embedding model instance.")
        return cls._instance