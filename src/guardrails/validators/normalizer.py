import re

from src.guardrails.base import BaseValidator


class QueryNormalizer(BaseValidator):

    def validate(self, state):

        query = state.get("query", "")

        query = re.sub(r"\s+", " ", query).strip()

        state["query"] = query

        return state