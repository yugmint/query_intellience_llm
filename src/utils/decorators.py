import time
from functools import wraps

from src.utils.logger import logger


def log_node(node_name: str):
    """
    Decorator for logging LangGraph node execution.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            start_time = time.perf_counter()

            logger.info("=" * 80)
            logger.info(f"[START] Node: {node_name}")

            try:

                result = func(*args, **kwargs)

                elapsed = time.perf_counter() - start_time

                logger.info(f"[DONE] Node: {node_name}")
                logger.info(f"[TIME] {elapsed:.4f} sec")

                return result

            except Exception as e:

                elapsed = time.perf_counter() - start_time

                logger.exception(f"[FAILED] Node: {node_name}")
                logger.info(f"[TIME] Failed After : {elapsed:.4f} sec")

                raise

        return wrapper

    return decorator