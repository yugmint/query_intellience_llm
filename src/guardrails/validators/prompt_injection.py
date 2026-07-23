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

        # Match against a whitespace-collapsed copy so padding (extra
        # spaces/tabs/newlines inside a blocked phrase, e.g. "ignore
        # previous  instructions") can't be used to dodge detection.
        # This validator runs before QueryNormalizer in InputGuardrail's
        # chain, so state["query"] itself is deliberately left untouched
        # here -- normalizing the actual query is still QueryNormalizer's
        # job, unchanged.
        normalized_query = re.sub(r"\s+", " ", query)

        for pattern in PATTERNS:

            if re.search(pattern, normalized_query):

                state["is_valid"] = False

                state["guardrail_reason"] = (
                    "Prompt injection detected."
                )

                break

        return state