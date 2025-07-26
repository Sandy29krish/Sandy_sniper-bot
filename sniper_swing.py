import os
import json
import logging
from datetime import datetime, time
import pytz
from utils.kite_api import place_order, exit_order
from utils.notifications import Notifier
from utils.swing_config import SYMBOLS, CAPITAL
from utils.lot_manager import get_swing_strike
from utils.nse_data import get_future_price, get_next_expiry_date
from utils.trade_logger import log_swing_trade
from utils.indicators import get_indicators_15m_30m
from utils.ai_assistant import analyze_trade_signal

STATE_FILE = "sniper_swing_state.json"
MAX_DAILY_TRADES = 3
MAX_SIMULTANEOUS_TRADES = 3

# Logger
def setup_logger():
    logger = logging.getLogger("SniperSwing")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler("sniper_swing.log")
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()

# State
class StateManager:
    def __init__(self, filename=STATE_FILE):
        self.filename = filename
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"positions": {}, "daily_trade_count": 0, "last_trade_date": None}

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.state, f)

    def reset_if_new_day(self):
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
        if self.state["last_trade_date"] != today:
            self.state["daily_trade_count"] = 0
            self.state["last_trade_date"] = today
            self.save()

class SniperSwingBot:
    def __init__(self, config, capital):
        self.config = config
        self.capital = capital
        self.notifier = Notifier(config["telegram_token"], config["telegram_id"])
        self.state = StateManager()

    def is_friday_315(self):
        now = datetime.now(pytz.timezone("Asia/Kolkata"))
        return now.weekday() == 4 and now.time() >= time(15, 15)

    def run(self):
        self.state.reset_if_new_day()

        if self.is_friday_315():
            logger.info("Forced exit at 3:15 PM Friday")
            for sym in list(self.state.state["positions"].keys()):
                self.exit_trade(sym)
            return

        if self.state.state["daily_trade_count"] >= MAX_DAILY_TRADES:
            logger.info("Max daily trades reached")
            return

        for symbol in SYMBOLS:
            if symbol in self.state.state["positions"]:
                if self.should_exit(symbol):
                    self.exit_trade(symbol)
                continue

            if len(self.state.state["positions"]) >= MAX_SIMULTANEOUS_TRADES:
                logger.info("Max simultaneous positions open")
                break

            signal, indicators = get_indicators_15m_30m(symbol)
            if not signal:
                continue

            if not (indicators["rsi"] > indicators["rsi_ma26"] and
                    indicators["ma_hierarchy"] and
                    indicators["pvi_positive"] and
                    indicators["lr_slope_positive"]):
                continue

            expiry = get_next_expiry_date(symbol)
            future_price = get_future_price(symbol)
            strike, premium = get_swing_strike(symbol, future_price, signal, expiry)
            lots = SYMBOLS[symbol]["lot_size"]
            quantity = self.calculate_lot_size(premium, lots)
            if quantity == 0:
                logger.warning(f"Lot size 0 for {symbol}, skipping.")
                continue

            reasoning = analyze_trade_signal(symbol, indicators, signal)

            try:
                place_order(
                    tradingsymbol=strike,
                    exchange="NFO",
                    quantity=quantity,
                    transaction_type="BUY" if signal == "bullish" else "SELL",
                    product="NRML",
                    order_type="MARKET"
                )
                self.state.state["positions"][symbol] = {
                    "signal": signal,
                    "entry_price": premium,
                    "strike": strike,
                    "expiry": expiry,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.state.state["daily_trade_count"] += 1
                self.state.save()
                msg = f"✅ {symbol} SWING {signal.upper()} ENTRY\nStrike: {strike}, Qty: {quantity}, Expiry: {expiry}\n\n🤖 Reason:\n{reasoning}"
                self.notifier.send_telegram(msg)
                log_swing_trade(symbol, signal, strike, premium, quantity, expiry, reasoning)
            except Exception as e:
                logger.error(f"Order failed: {e}")
                self.notifier.send_telegram(f"Order failed: {e}")

    def calculate_lot_size(self, premium, lot_size):
        capital_per_trade = self.capital / MAX_DAILY_TRADES
        return int(capital_per_trade / (premium * lot_size)) * lot_size

    def should_exit(self, symbol):
        data = self.state.state["positions"].get(symbol)
        if not data:
            return False
        current_price = premium = data["entry_price"]  # Replace with actual LTP fetcher if needed
        signal = data["signal"]

        if signal == "bullish" and current_price < premium * 0.95:
            return True
        if signal == "bearish" and current_price > premium * 1.05:
            return True

        return False

    def exit_trade(self, symbol):
        data = self.state.state["positions"].get(symbol)
        if not data:
            return
        try:
            exit_order(
                tradingsymbol=data["strike"],
                exchange="NFO",
                quantity=SYMBOLS[symbol]["lot_size"],
                transaction_type="SELL" if data["signal"] == "bullish" else "BUY",
                product="NRML",
                order_type="MARKET"
            )
            msg = f"🚪 EXITED {symbol} position"
            self.notifier.send_telegram(msg)
            self.state.state["positions"].pop(symbol, None)
            self.state.save()
        except Exception as e:
            logger.error(f"Exit failed: {e}")
            self.notifier.send_telegram(f"Exit failed: {e}")

# ✅ THIS IS THE FINAL WRAPPER REQUIRED FOR runner.py TO WORK
def run_swing_strategy(capital, config):
    bot = SniperSwingBot(config=config, capital=capital)
    bot.run()

if __name__ == "__main__":
    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    capital = float(os.getenv("CAPITAL", CAPITAL))
    bot = SniperSwingBot(config, capital)
    try:
        while True:
            bot.run()
    except KeyboardInterrupt:
        bot.state.save()
        logger.info("Sniper Swing stopped.")
