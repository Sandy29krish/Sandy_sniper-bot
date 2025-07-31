import threading
import time
import logging
import sys
import os
from kiteconnect import KiteConnect, KiteException

# Add root directory to path for telegram_commands import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telegram_commands import send_telegram_message

logger = logging.getLogger(__name__)

class KiteWatchdog(threading.Thread):
    def __init__(self, kite: KiteConnect, check_interval=60, max_retries=5):
        super().__init__()
        self.kite = kite
        self.check_interval = check_interval
        self.max_retries = max_retries
        self.running = True
        self.retry_count = 0
        self.telegram_retry_count = 0

    def run(self):
        while self.running:
            try:
                # Check Kite API connection
                self.kite.profile()
                logger.info("Kite API connection is healthy.")
                self.retry_count = 0
            except KiteException as e:
                logger.warning(f"Kite API connection failed: {e}")
                self.retry_count += 1
                if self.retry_count > self.max_retries:
                    msg = f"Kite API connection failed {self.retry_count} times. Please check VPS/internet."
                    self.safe_send_telegram(msg)
                    logger.error(msg)
                    self.retry_count = 0
                else:
                    self.try_reconnect()

            # Check Telegram health
            if not self.check_telegram():
                self.telegram_retry_count += 1
                if self.telegram_retry_count > self.max_retries:
                    msg = f"Telegram alerts not sending for {self.telegram_retry_count} attempts."
                    logger.error(msg)
                    # Could send email or alert via another method here
                    self.telegram_retry_count = 0
                else:
                    self.safe_send_telegram("Attempting to restore Telegram alerts...")

            else:
                self.telegram_retry_count = 0

            time.sleep(self.check_interval)

    def try_reconnect(self):
        logger.info("Attempting to reconnect Kite API...")
        try:
            self.kite = refresh_kite_instance()
            self.safe_send_telegram("Kite API reconnected successfully.")
            logger.info("Reconnected Kite API successfully.")
            self.retry_count = 0
        except Exception as e:
            logger.error(f"Reconnection attempt failed: {e}")

    def check_telegram(self):
        try:
            return check_telegram_health()
        except Exception as e:
            logger.error(f"Telegram health check failed: {e}")
            return False

    def safe_send_telegram(self, message):
        try:
            send_telegram_message(message)
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    def stop(self):
        self.running = False

def refresh_kite_instance():
    from utils.auto_token_refresher import perform_auto_login
    kite = perform_auto_login()
    return kite

