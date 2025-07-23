import threading
import logging
import signal
import sys
from core.sniper_swing import SniperSwing
from utils.swing_config import SWING_CONFIG
from utils.telegram_commands import start_telegram_command_server
from utils.auto_token_refresher import start_token_refresher
from utils.system_health_monitor import start_system_health_monitor

def run_swing_bot():
    bot = SniperSwing(capital=SWING_CONFIG.get("capital", 170000), config=SWING_CONFIG)
    while True:
        try:
            bot.run()
        except Exception as e:
            logging.error(f"Error in bot.run(): {e}", exc_info=True)

def shutdown(signal_received, frame):
    logging.info("Shutdown signal received. Exiting gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    start_token_refresher()
    start_system_health_monitor()

    telegram_thread = threading.Thread(target=start_telegram_command_server, daemon=True)
    telegram_thread.start()

    run_swing_bot()