from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class EvaluationResult:
    query: str
    category: str
    response: str
    latency: float
    success: bool
    metadata: dict[str, Any]

    def to_dict(self):
        return asdict(self)