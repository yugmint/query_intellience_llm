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
            logger.info(f"🚀 Node Started : {node_name}")

            try:

                result = func(*args, **kwargs)

                elapsed = time.perf_counter() - start_time

                logger.info(f"✅ Node Completed : {node_name}")
                logger.info(f"⏱ Execution Time : {elapsed:.4f} sec")

                return result

            except Exception as e:

                elapsed = time.perf_counter() - start_time

                logger.exception(f"❌ Node Failed : {node_name}")
                logger.info(f"⏱ Failed After : {elapsed:.4f} sec")

                raise

        return wrapper

    return decorator