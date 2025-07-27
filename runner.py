# runner.py

import os
import time
import argparse
import logging
import signal
import sys
import threading
import yaml
from sniper_swing import run_swing_strategy  # ✅ Main bot function
from utils.swing_config import CAPITAL
from utils.auto_token_refresher import start_token_refresher  # ✅ Token refresh loop
from logging.handlers import RotatingFileHandler

# Global shutdown event for graceful shutdown
shutdown_event = threading.Event()

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Sniper Swing Bot.")
    parser.add_argument('--capital', type=float, default=float(os.getenv("CAPITAL", CAPITAL)),
                        help="Trading capital to use")
    parser.add_argument('--sleep', type=int, default=int(os.getenv("SLEEP_INTERVAL", 60)),
                        help="Sleep duration between runs (seconds)")
    parser.add_argument('--config', type=str, default="config.yaml",
                        help="Configuration file path")
    return parser.parse_args()

def load_config(config_path):
    """Load configuration with proper error handling"""
    try:
        if not os.path.exists(config_path):
            logging.warning(f"Config file {config_path} not found, using environment variables")
            return {
                "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN"),
                "telegram_id": os.getenv("TELEGRAM_ID")
            }
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        # Ensure required fields are present
        config.setdefault("telegram_token", os.getenv("TELEGRAM_BOT_TOKEN"))
        config.setdefault("telegram_id", os.getenv("TELEGRAM_ID"))
        
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        # Fallback to environment variables
        return {
            "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "telegram_id": os.getenv("TELEGRAM_ID")
        }

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
    shutdown_event.set()

def run_bot_loop(capital, config, sleep_interval):
    """Main bot execution loop with proper error handling"""
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while not shutdown_event.is_set():
        try:
            logging.info("🔄 Starting bot run...")
            run_swing_strategy(capital=capital, config=config)
            logging.info("✅ Bot run completed successfully.")
            consecutive_errors = 0  # Reset error counter on success
            
        except KeyboardInterrupt:
            logging.info("⛔ Received keyboard interrupt.")
            shutdown_event.set()
            break
            
        except Exception as e:
            consecutive_errors += 1
            logging.exception(f"⚠️ Error during bot run ({consecutive_errors}/{max_consecutive_errors}): %s", e)
            
            # If too many consecutive errors, increase sleep time
            if consecutive_errors >= max_consecutive_errors:
                error_sleep = min(sleep_interval * 3, 300)  # Max 5 minutes
                logging.warning(f"Too many consecutive errors. Sleeping for {error_sleep} seconds...")
                if shutdown_event.wait(error_sleep):
                    break
                consecutive_errors = 0  # Reset after extended sleep
        
        # Normal sleep between runs
        if not shutdown_event.is_set():
            logging.info(f"💤 Sleeping for {sleep_interval} seconds...")
            if shutdown_event.wait(sleep_interval):
                break

def main():
    # Setup logging with better formatting
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('runner.log', maxBytes=10*1024*1024, backupCount=3)
        ]
    )

    # Parse arguments
    args = parse_args()
    logging.info("🚀 Starting Sniper Swing Bot with capital: ₹%s", args.capital)
    
    # Load configuration
    config = load_config(args.config)
    if not config.get("telegram_token") or not config.get("telegram_id"):
        logging.warning("⚠️ Telegram configuration missing. Notifications may not work.")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Start auto token refresher
    logging.info("🔄 Starting Kite token refresher in background...")
    try:
        token_thread, token_stop_event = start_token_refresher()
        logging.info("✅ Token refresher started successfully.")
    except Exception as e:
        logging.error("❌ Failed to start token refresher: %s", e)
        logging.warning("⚠️ Continuing without token refresher. Manual token management required.")
        token_thread, token_stop_event = None, None

    try:
        # Run main bot loop
        run_bot_loop(args.capital, config, args.sleep)
        
    except Exception as e:
        logging.critical("🔥 Fatal error in main: %s", e, exc_info=True)
        
    finally:
        logging.info("🛑 Shutting down gracefully...")
        
        # Stop token refresher if it was started
        if token_stop_event:
            token_stop_event.set()
            logging.info("⏹️ Token refresher stop signal sent.")
            
        # Wait a bit for threads to finish
        if token_thread and token_thread.is_alive():
            token_thread.join(timeout=5)
            if token_thread.is_alive():
                logging.warning("⚠️ Token refresher thread did not stop gracefully.")
        
        logging.info("👋 Bot exited gracefully.")

if __name__ == "__main__":
    main()
