import re

from src.guardrails.base import BaseValidator


PATTERNS = [

    r"ignore previous instructions",

    r"forget previous instructions",

    r"system prompt",

    r"developer mode",

    r"act as",

    r"jailbreak",

]


class PromptInjectionValidator(BaseValidator):

    def validate(self, state):

        query = state.get("query", "").lower()

        for pattern in PATTERNS:

            if re.search(pattern, query):

                state["is_valid"] = False

                state["guardrail_reason"] = (
                    "Prompt injection detected."
                )

                break

        return state