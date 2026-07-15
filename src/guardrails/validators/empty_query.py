from src.guardrails.base import BaseValidator


class EmptyQueryValidator(BaseValidator):

    def validate(self, state):

        query = state.get("query", "").strip()

        if not query:

            state["is_valid"] = False

            state["guardrail_reason"] = (
                "EmptyQueryValidator: query is empty."
)

        return state