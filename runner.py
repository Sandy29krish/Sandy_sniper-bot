from sniper_swing import SniperSwing
from utils.swing_config import SWING_CONFIG
import time

bot = SniperSwing(capital=170000, config=SWING_CONFIG)

while True:
    bot.run()
    time.sleep(30)  # Adjust sleep time as needed (e.g. 30 seconds or aligned with candle timeframe)
