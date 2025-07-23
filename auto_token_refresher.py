import threading
import time
import logging
from utils.zerodha_auto_login import perform_auto_login  # Your TOTP-based login script
from utils.kite_api import kite  # Your KiteConnect instance

REFRESH_INTERVAL = 60 * 15  # 15 minutes, adjust as needed

def token_refresher_loop():
    while True:
        try:
            new_access_token = perform_auto_login()
            kite.set_access_token(new_access_token)
            logging.info("Access token refreshed successfully.")
        except Exception as e:
            logging.error(f"Failed to refresh access token: {e}")
        time.sleep(REFRESH_INTERVAL)

def start_token_refresher():
    thread = threading.Thread(target=token_refresher_loop, daemon=True)
    thread.start()
