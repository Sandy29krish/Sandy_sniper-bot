import threading
import time
import logging
from typing import Optional, Callable
from utils.zerodha_auto_login import perform_auto_login  # Your TOTP-based login script
from utils.kite_api import kite  # Your KiteConnect instance

DEFAULT_REFRESH_INTERVAL = 60 * 15  # 15 minutes

def token_refresher_loop(
    refresh_interval: int = DEFAULT_REFRESH_INTERVAL,
    backoff_factor: float = 2.0,
    max_backoff: int = 60 * 60,  # 1 hour
    stop_event: Optional[threading.Event] = None,
    logger: Optional[logging.Logger] = None,
    on_success: Optional[Callable] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
):
    """
    Periodically refreshes the Kite API access token.

    Args:
        refresh_interval (int): Interval (in seconds) between refresh attempts.
        backoff_factor (float): Multiplicative factor for exponential backoff.
        max_backoff (int): Maximum backoff time in seconds.
        stop_event (threading.Event): Event to support graceful shutdown.
        logger (logging.Logger): Custom logger instance.
        on_success (callable): Optional callback on successful refresh.
        on_failure (callable): Optional callback on refresh failure.
    """
    _logger = logger or logging.getLogger(__name__)
    current_interval = refresh_interval

    while not (stop_event and stop_event.is_set()):
        try:
            new_access_token = perform_auto_login()
            kite.set_access_token(new_access_token)
            _logger.info("Access token refreshed successfully.")
            if on_success:
                on_success()
            current_interval = refresh_interval  # Reset delay after success
        except Exception as e:
            _logger.error(f"Failed to refresh access token: {e}", exc_info=True)
            if on_failure:
                on_failure(e)
            current_interval = min(current_interval * backoff_factor, max_backoff)
            _logger.info(f"Backing off. Next retry in {current_interval} seconds.")
        # Wait, but check stop_event periodically for graceful shutdown
        start_time = time.time()
        while time.time() - start_time < current_interval:
            if stop_event and stop_event.is_set():
                _logger.info("Token refresher loop received stop signal. Exiting...")
                return
            time.sleep(1)

def start_token_refresher(
    refresh_interval: int = DEFAULT_REFRESH_INTERVAL,
    **kwargs
) -> threading.Thread:
    """
    Starts the token refresher loop in a daemon thread.
    Returns the thread instance for possible control (e.g., join, stop).
    """
    stop_event = kwargs.pop('stop_event', threading.Event())
    thread = threading.Thread(
        target=token_refresher_loop,
        kwargs={'refresh_interval': refresh_interval, 'stop_event': stop_event, **kwargs},
        daemon=True
    )
    thread.start()
    return thread, stop_event

# Example usage:
# thread, stop_event = start_token_refresher()
# ... when you want to stop: stop_event.set(); thread.join()
