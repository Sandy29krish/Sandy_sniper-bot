import os
import time
import argparse
import logging
from sniper_swing import run_swing_strategy
from utils.swing_config import SWING_CONFIG

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Sniper Swing Bot.")
    parser.add_argument('--capital', type=float, default=float(os.getenv("CAPITAL", 170000)),
                        help="Trading capital to use")
    parser.add_argument('--sleep', type=int, default=int(os.getenv("SLEEP_INTERVAL", 30)),
                        help="Sleep duration between runs (seconds)")
    return parser.parse_args()

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

    args = parse_args()
    bot = SniperSwing(capital=args.capital, config=SWING_CONFIG)
    logging.info("Starting Sniper Swing Bot with capital: %s", args.capital)

    try:
        while True:
            try:
                bot.run()
                logging.info("Bot run completed successfully.")
            except Exception as e:
                logging.exception("Error during bot run: %s", e)
            time.sleep(args.sleep)
    except KeyboardInterrupt:
        logging.info("Sniper Swing Bot stopped by user.")
    except Exception as e:
        logging.critical("Fatal error: %s", e)
    finally:
        logging.info("Bot exiting gracefully.")

if __name__ == "__main__":
    main()
