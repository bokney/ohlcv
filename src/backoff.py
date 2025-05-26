
import logging
from time import sleep
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def backoff(
    delay: int = 1,
    retries: int = 4,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if not isinstance(delay, (int, float)) or delay < 0:
        raise ValueError(
            f"Invalid delay {delay!r}: must be a non-negative number."
        )
    if not isinstance(retries, int) or retries < 1:
        raise ValueError(
            f"Invalid retries {retries!r}: must be an integer >= 1."
        )

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_retry = 0
            current_delay = delay
            while current_retry < retries:
                try:
                    return func(*args, **kwargs)
                except ValueError:
                    raise
                except Exception as e:
                    current_retry += 1
                    if current_retry >= retries:
                        logger.error(
                            f"{func.__name__} failed after {retries} "
                            f"retries. Last error: {e}"
                        )
                        raise
                    logger.warning(
                        f"{func.__name__} failed (attempt "
                        f"{current_retry}/{retries}): {e}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    sleep(current_delay)
                    current_delay *= 2
        return wrapper
    return decorator
