import logging
import time
import traceback

def auto_error_fixer(func, retry_delay=5, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            logging.error(f"Error occurred: {e}\n{traceback.format_exc()}")
            retries += 1
            logging.info(f"Retrying {func.__name__} in {retry_delay} seconds... Attempt {retries} of {max_retries}")
            time.sleep(retry_delay)
    logging.error(f"Max retries reached for {func.__name__}. Giving up.")
    return None
