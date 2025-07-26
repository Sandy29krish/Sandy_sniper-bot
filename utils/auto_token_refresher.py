import threading
import time
import logging
from typing import Optional, Callable
from utils.zerodha_auth import perform_auto_login  # Ensure this file is correct
from utils.kite_api import kite  # Your global Kite instance

# Refresh interval: 15 minutes
DEFAULT_REFRESH_INTERVAL = 60 * 15  # 15 min in seconds

def token_refresher_loop(
    refresh_interval: int = DEFAULT_REFRESH_INTERVAL,
    backoff_factor: float = 2.0,
    max_backoff: int = 60 * 60,  # Max retry interval: 1 hour
    stop_event: Optional[threading.Event] = None,
    logger: Optional[logging.Logger] = None,
    on_success: Optional[Callable] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
):
    """
    Periodically refreshes Zerodha Kite access token and exports it.
    """
    _logger = logger or logging.getLogger(__name__)
    current_interval = refresh_interval

    while not (stop_event and stop_event.is_set()):
        try:
            new_access_token = perform_auto_login()
            kite.set_access_token(new_access_token)

            # Save token to reusable shell file
            with open("/root/.kite_token_env", "w") as f:
                f.write(f'export KITE_ACCESS_TOKEN="{new_access_token}"\n')

            _logger.info("✅ Access token refreshed and exported successfully.")
            if on_success:
                on_success()
            current_interval = refresh_interval  # Reset on success

        except Exception as e:
            _logger.error(f"❌ Token refresh failed: {e}", exc_info=True)
            if on_failure:
                on_failure(e)
            current_interval = min(current_interval * backoff_factor, max_backoff)
            _logger.info(f"Retrying in {int(current_interval)} seconds...")

        # Wait, but break early if stop signal received
        start_time = time.time()
        while time.time() - start_time < current_interval:
            if stop_event and stop_event.is_set():
                _logger.info("❌ Token refresher received stop signal. Exiting.")
                return
            time.sleep(1)

def start_token_refresher(
    refresh_interval: int = DEFAULT_REFRESH_INTERVAL,
    **kwargs
) -> threading.Thread:
    """
    Starts the token refresher loop in background daemon thread.
    """
    stop_event = kwargs.pop('stop_event', threading.Event())
    thread = threading.Thread(
        target=token_refresher_loop,
        kwargs={'refresh_interval': refresh_interval, 'stop_event': stop_event, **kwargs},
        daemon=True
    )
    thread.start()
    return thread, stop_event

# Optional standalone run
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    thread, stop_event = start_token_refresher()
    try:
        while thread.is_alive():
            thread.join(timeout=1)
    except KeyboardInterrupt:
        stop_event.set()
        logging.info("🚦 Gracefully shutting down...")
        thread.join()
