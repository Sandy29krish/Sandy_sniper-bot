import threading
import logging
import signal
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from core.sniper_swing import SniperSwing
from utils.swing_config import SWING_CONFIG
from utils.telegram_commands import start_telegram_command_server
from utils.auto_token_refresher import start_token_refresher
from utils.system_health_monitor import start_system_health_monitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

shutdown_event = threading.Event()

def run_swing_bot():
    capital = int(os.getenv("SWING_BOT_CAPITAL", SWING_CONFIG.get("capital", 170000)))
    bot = SniperSwing(capital=capital, config=SWING_CONFIG)
    while not shutdown_event.is_set():
        try:
            bot.run()
        except Exception as e:
            logging.error(f"Error in bot.run(): {e}", exc_info=True)
            # Optional: sleep or backoff before retrying
        # Optional: add a small sleep to avoid tight loop on failure
        # time.sleep(1)

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
        # If you want to wait for threads (if not daemon), join here
        # token_thread.join()
        # health_thread.join()
        # telegram_thread.join()
        sys.exit(0)