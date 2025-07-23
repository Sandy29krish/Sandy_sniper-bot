import logging
import os
import json
from datetime import datetime
from utils.indicators import calculate_mas, calculate_rsi, calculate_lr_slope, calculate_pvi
from utils.trading import TradingAPI
from utils.notifications import Notifier

STATE_FILE = "bot_state.json"

def setup_logger():
    logger = logging.getLogger("SniperSwing")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("sniper_swing.log")
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class StateManager:
    """Handles saving/loading bot state for persistence."""
    def __init__(self, filename=STATE_FILE):
        self.filename = filename

    def load(self):
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return {"positions": {}, "prev_closes": {}}

    def save(self, state):
        with open(self.filename, "w") as f:
            json.dump(state, f)

class SniperSwing:
    """
    Swing trading bot using CPR, Moving Averages, RSI, and PVI.
    """
    def __init__(self, config, capital, logger):
        self.symbols = config["symbols"]
        self.capital = capital
        self.config = config
        self.logger = logger
        self.trading_api = TradingAPI(config["api_key"], config["api_secret"])
        self.notifier = Notifier(config["telegram_token"], config["telegram_chat_id"])
        self.state_manager = StateManager()
        # Load persistent state
        state = self.state_manager.load()
        self.positions = state.get("positions", {})
        self.prev_closes = state.get("prev_closes", {})

    def fetch_data(self, symbol):
        try:
            price = self.trading_api.get_price(symbol)
            mas = calculate_mas(symbol)
            rsi = calculate_rsi(symbol)
            slope = calculate_lr_slope(symbol)
            pvi = calculate_pvi(symbol)
            return price, mas, rsi, slope, pvi
        except Exception as e:
            self.logger.error(f"Data fetch error for {symbol}: {e}")
            self.notifier.send_telegram(f"Data fetch error for {symbol}: {e}")
            return None, None, None, None, None

    def swing_cpr_signal(self, symbol, price, cpr, prev_close):
        # CPR logic (simplified for illustration)
        if price > cpr["top"]:
            return "resistance"
        elif price < cpr["bottom"]:
            return "support"
        elif prev_close and prev_close < cpr["bottom"] and price > cpr["bottom"]:
            return "breakout"
        elif prev_close and prev_close > cpr["top"] and price < cpr["top"]:
            return "breakdown"
        return None

    def swing_ma_signal(self, mas, price, prev_close):
        # MA logic (simplified for illustration)
        if price > mas["ma20"]:
            return "resistance"
        elif price < mas["ma20"]:
            return "support"
        elif prev_close and prev_close < mas["ma20"] and price > mas["ma20"]:
            return "breakout"
        elif prev_close and prev_close > mas["ma20"] and price < mas["ma20"]:
            return "breakdown"
        return None

    def check_entry_conditions(self, symbol, price, mas, rsi, slope, pvi):
        # Example: bullish entry
        if (price > mas["ma20"] and
            mas["ma20"] > mas["ma50"] > mas["ma100"] and
            rsi["rsi2"] > 50 and rsi["rsi5"] > 50 and
            pvi > 0 and slope > 0):
            return "bullish"
        # Example: bearish entry
        if (price < mas["ma20"] and
            mas["ma20"] < mas["ma50"] < mas["ma100"] and
            rsi["rsi2"] < 50 and rsi["rsi5"] < 50 and
            pvi < 0 and slope < 0):
            return "bearish"
        return None

    def enter_trade(self, symbol, direction, price):
        amount = self.capital / len(self.symbols)
        try:
            order = self.trading_api.place_order(symbol, direction, amount)
            self.positions[symbol] = {"direction": direction, "entry_price": price, "timestamp": datetime.utcnow().isoformat()}
            self.logger.info(f"Entered {direction} trade on {symbol} at {price}")
            self.notifier.send_telegram(f"Entered {direction} trade on {symbol} at {price}")
            self.save_state()
        except Exception as e:
            self.logger.error(f"Trade entry failure for {symbol}: {e}")
            self.notifier.send_telegram(f"Trade entry failure for {symbol}: {e}")

    def check_exit_conditions(self, symbol, price):
        # Placeholder: Implement your actual exit logic
        pos = self.positions.get(symbol)
        if not pos:
            return False
        # Example: exit if price moves 2% against position
        entry = pos["entry_price"]
        if pos["direction"] == "bullish" and price < entry * 0.98:
            return True
        if pos["direction"] == "bearish" and price > entry * 1.02:
            return True
        return False

    def exit_trade(self, symbol, price):
        try:
            self.trading_api.close_position(symbol)
            self.logger.info(f"Exited trade on {symbol} at {price}")
            self.notifier.send_telegram(f"Exited trade on {symbol} at {price}")
            self.positions.pop(symbol, None)
            self.save_state()
        except Exception as e:
            self.logger.error(f"Trade exit failure for {symbol}: {e}")
            self.notifier.send_telegram(f"Trade exit failure for {symbol}: {e}")

    def save_state(self):
        self.state_manager.save({"positions": self.positions, "prev_closes": self.prev_closes})

    def run(self):
        for symbol in self.symbols:
            price, mas, rsi, slope, pvi = self.fetch_data(symbol)
            if not all([price, mas, rsi, slope, pvi]):
                continue  # Skip iteration on data failure

            prev_close = self.prev_closes.get(symbol)
            self.prev_closes[symbol] = price

            # Exit logic
            if symbol in self.positions:
                if self.check_exit_conditions(symbol, price):
                    self.exit_trade(symbol, price)
                continue

            # Entry logic
            direction = self.check_entry_conditions(symbol, price, mas, rsi, slope, pvi)
            if direction:
                self.enter_trade(symbol, direction, price)

# Example usage:
if __name__ == "__main__":
    import yaml

    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    logger = setup_logger()
    capital = float(os.getenv("CAPITAL", 100000))
    bot = SniperSwing(config, capital, logger)
    try:
        while True:
            bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user. Exiting gracefully.")
        bot.save_state()