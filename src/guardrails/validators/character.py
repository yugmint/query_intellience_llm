import re

from src.guardrails.base import BaseValidator


class CharacterValidator(BaseValidator):

    def validate(self, state):

        query = state.get("query", "")

        query = re.sub(r"[\x00-\x1f\x7f]", "", query)

        state["query"] = query

        return state