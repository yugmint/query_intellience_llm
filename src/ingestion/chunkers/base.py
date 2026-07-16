from abc import ABC, abstractmethod

from langchain_core.documents import Document


class BaseChunker(ABC):
    """
    Base interface for every chunking strategy.
    """

    @abstractmethod
    def chunk(
        self,
        documents: list[Document],
    ) -> list[Document]:

        raise NotImplementedError