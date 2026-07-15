from src.guardrails.base import BaseValidator
from src.utils.logger import logger

MAX_QUERY_LENGTH = 512


class LengthValidator(BaseValidator):

    def validate(self, state):

        query = state.get("query", "").strip()

        length = len(query)

        logger.info(f"Query Length : {length}")

        if length > MAX_QUERY_LENGTH:

            state["is_valid"] = False

            state["guardrail_reason"] = (
                f"LengthValidator: query exceeds "
                f"{MAX_QUERY_LENGTH} characters."
            )

            logger.warning(state["guardrail_reason"])

        return state