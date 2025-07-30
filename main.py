import threading
import logging
import signal
import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from sniper_swing import SniperSwingBot
from utils.swing_config import SWING_CONFIG, CAPITAL
from telegram_commands import start_telegram_command_server
from utils.auto_token_refresher import start_token_refresher
from system_health_monitor import start_system_health_monitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

shutdown_event = threading.Event()

def run_swing_bot():
    capital = int(os.getenv("SWING_BOT_CAPITAL", CAPITAL))
    bot = SniperSwingBot(config=SWING_CONFIG, capital=capital)
    while not shutdown_event.is_set():
        try:
            bot.run()
        except Exception as e:
            logging.error(f"Error in bot.run(): {e}", exc_info=True)
        # Sleep to avoid tight loop and excessive logging
        time.sleep(30)  # 30 seconds between cycles

def handle_shutdown(signum, frame):
    logging.info("Shutdown signal received. Stopping all services...")
    shutdown_event.set()

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Start background services
    token_thread = threading.Thread(target=start_token_refresher, daemon=True)
    health_thread = threading.Thread(target=start_system_health_monitor, daemon=True)
    telegram_thread = threading.Thread(target=start_telegram_command_server, daemon=True)

    token_thread.start()
    health_thread.start()
    telegram_thread.start()

    try:
        run_swing_bot()
    except Exception as e:
        logging.error(f"Fatal error in main loop: {e}", exc_info=True)
    finally:
        logging.info("Main thread exiting. Waiting for background threads to finish...")
        sys.exit(0)