# src/retrieval/reranker.py

from typing import Any, Optional

from src.retrieval.config import RERANK_MODEL
from src.utils.logger import logger


class RerankerFactory:
    """
    Factory for the cross-encoder reranker model. Singleton, same pattern
    as EmbeddingFactory/LLMFactory -- loading a cross-encoder is not free,
    reuse the one instance across requests.
    """

    _instance: Optional[Any] = None

    @classmethod
    def get(cls):

        if cls._instance is None:

            # Imported lazily so importing this module doesn't force a
            # sentence_transformers import (and the model download) for
            # code paths that never rerank.
            from sentence_transformers import CrossEncoder

            logger.info("=" * 80)
            logger.info("Initializing Reranker")
            logger.info(f"Model : {RERANK_MODEL}")

            cls._instance = CrossEncoder(RERANK_MODEL)

            logger.info("Reranker initialized successfully.")

        else:
            logger.debug("Reusing existing reranker instance.")

        return cls._instance

    @classmethod
    def build(cls):
        return cls.get()
