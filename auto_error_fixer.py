import logging
import time
import traceback
from functools import wraps

def auto_error_fixer(
    retry_delay=5,
    max_retries=3,
    exceptions=(Exception,),
    backoff=False,
    raise_on_failure=False,
    logger=None
):
    """
    Decorator to retry a function upon exception.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(__name__)
            delay = retry_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    _logger.error(f"Error in {func.__name__}: {e}\n{traceback.format_exc()}")
                    if attempt == max_retries:
                        _logger.error(f"Max retries reached for {func.__name__}.")
                        if raise_on_failure:
                            raise
                        return None
                    _logger.info(f"Retry {attempt}/{max_retries} in {delay} seconds...")
                    time.sleep(delay)
                    if backoff:
                        delay *= 2
        return wrapper
    return decorator