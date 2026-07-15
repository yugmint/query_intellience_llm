from abc import ABC, abstractmethod

from src.workflow.state import RAGState


class BaseValidator(ABC):
    """
    Base class for all guardrail validators.
    """

    @abstractmethod
    def validate(self, state: RAGState) -> RAGState:
        """
        Validate and optionally modify the workflow state.
        """
        pass