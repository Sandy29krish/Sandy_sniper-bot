import os
import time
import threading
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils.zerodha_auth import perform_auto_login
from utils.kite_api import kite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REFRESH_INTERVAL = 15 * 60  # 15 minutes

def auto_refresh_token():
    while True:
        try:
            logger.info("🔄 Attempting token refresh...")

            success = perform_auto_login()
            if success:
                logger.info("✅ Token refreshed successfully.")
            else:
                logger.error("❌ Token refresh failed. Check credentials or network.")

        except Exception as e:
            logger.error(f"❌ Exception during auto login: {e}")

        logger.info("💤 Sleeping 15 mins before next token refresh...")
        time.sleep(REFRESH_INTERVAL)


def start_auto_token_refresher():
    thread = threading.Thread(target=auto_refresh_token)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    start_auto_token_refresher()

    # Keep the main thread alive
    while True:
        time.sleep(60)
