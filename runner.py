import os
import time
import argparse
import logging
from sniper_swing import run_swing_strategy  # ✅ function, not class
from utils.swing_config import SWING_CONFIG

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Sniper Swing Bot.")
    parser.add_argument('--capital', type=float, default=float(os.getenv("CAPITAL", 170000)),
                        help="Trading capital to use")
    parser.add_argument('--sleep', type=int, default=int(os.getenv("SLEEP_INTERVAL", 60)),
                        help="Sleep duration between runs (seconds)")
    return parser.parse_args()

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

    args = parse_args()
    logging.info("🚀 Starting Sniper Swing Bot with capital: ₹%s", args.capital)

    config = {
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_id": os.getenv("TELEGRAM_ID")
    }

    try:
        while True:
            try:
                run_swing_strategy(capital=args.capital, config=config)
                logging.info("✅ Bot run completed.")
            except Exception as e:
                logging.exception("⚠️ Error during bot run: %s", e)
            time.sleep(args.sleep)
    except KeyboardInterrupt:
        logging.info("⛔ Sniper Swing Bot stopped by user.")
    except Exception as e:
        logging.critical("🔥 Fatal error: %s", e)
    finally:
        logging.info("🛑 Bot exiting gracefully.")

if __name__ == "__main__":
    main()
