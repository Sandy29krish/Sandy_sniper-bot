import time
from sniper_swing import SniperSwing
from utils.swing_config import SWING_CONFIG

def main():
    capital = 170000  # Your trading capital
    bot = SniperSwing(capital=capital, config=SWING_CONFIG)
    print("Starting Sniper Swing Bot...")

    try:
        while True:
            bot.run()
            time.sleep(30)  # Adjust sleep duration as per your strategy timeframe
    except KeyboardInterrupt:
        print("Sniper Swing Bot stopped by user.")

if __name__ == "__main__":
    main()
