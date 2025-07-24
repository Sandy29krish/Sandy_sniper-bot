import os
import json
import logging
from datetime import datetime, time
import pytz
import pandas as pd
import numpy as np
from utils.trading import TradingAPI
from utils.notifications import Notifier

STATE_FILE = "sniper_swing_state.json"

MAX_SIMULTANEOUS_TRADES = 3
MAX_DAILY_TRADES = 3

# Setup logger
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

# Indicator calculation helpers
def calculate_mas(df):
    df['ma3'] = df['typical_price'].rolling(3).mean()
    df['ma9'] = df['typical_price'].ewm(span=9, adjust=False).mean()
    df['ma20'] = df['typical_price'].rolling(20).mean()
    df['ma50'] = df['high'].ewm(span=50, adjust=False).mean()
    df['ma200'] = df['high'].rolling(200).mean()
    return df

def calculate_rsi(df, period=14):
    delta = df['typical_price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    # RSI moving averages
    df['rsi_ma9'] = df['rsi'].rolling(9).mean()
    df['rsi_ma14'] = df['rsi'].rolling(14).mean()
    df['rsi_ma26'] = df['rsi'].rolling(26).mean()
    return df

def calculate_lr_slope(df, period=21):
    # Linear Regression slope of high prices over period
    from numpy.polynomial.polynomial import polyfit
    slopes = []
    for i in range(len(df)):
        if i < period:
            slopes.append(np.nan)
            continue
        y = df['high'].iloc[i-period:i]
        x = np.arange(period)
        b, m = polyfit(x, y, 1)
        slopes.append(m)
    df['lr_slope'] = slopes
    return df

def calculate_pvi(df):
    # Price Volume Indicator (simple version)
    pvi = [np.nan]
    for i in range(1, len(df)):
        if df['volume'].iloc[i] > df['volume'].iloc[i-1]:
            pvi.append(pvi[-1] + ((df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]) * 100)
        else:
            pvi.append(pvi[-1])
    df['pvi'] = pvi
    return df

# CPR calculation (example placeholder, replace with your method)
def calculate_cpr(df):
    # Simple CPR as midpoint between pivot points (placeholder)
    df['cpr_top'] = (df['pivot_r1'] + df['pivot_r2']) / 2 if 'pivot_r1' in df.columns else np.nan
    df['cpr_bottom'] = (df['pivot_s1'] + df['pivot_s2']) / 2 if 'pivot_s1' in df.columns else np.nan
    return df

# State manager class for persistence
class StateManager:
    def __init__(self, filename=STATE_FILE):
        self.filename = filename
        self.state = self.load_state()

    def load_state(self):
        if os.path.isfile(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state file: {e}")
        return {
            "positions": {},
            "daily_trade_count": 0,
            "last_trade_date": None
        }

    def save_state(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.state, f)
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")

    def reset_daily_count_if_new_day(self):
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        today_str = now.strftime("%Y-%m-%d")
        if self.state["last_trade_date"] != today_str:
            self.state["daily_trade_count"] = 0
            self.state["last_trade_date"] = today_str
            logger.info("Reset daily trade count for new day")
            self.save_state()

class SniperSwingBot:
    def __init__(self, config, capital):
        self.config = config
        self.capital = capital
        self.api = TradingAPI(config["api_key"], config["api_secret"])
        self.notifier = Notifier(config["telegram_token"], config["telegram_chat_id"])
        self.state_manager = StateManager()
        self.positions = self.state_manager.state.get("positions", {})
        self.daily_trade_count = self.state_manager.state.get("daily_trade_count", 0)

    def is_friday_315pm(self):
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        return now.weekday() == 4 and now.time() >= time(15, 15)

    def fetch_historical_data(self, symbol, from_date, to_date, interval="3minute"):
        # Implement actual historical fetch from Kite API
        # Return DataFrame with columns: open, high, low, close, volume, typical_price
        pass  # Placeholder

    def prepare_indicators(self, df):
        df['typical_price'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        df = calculate_mas(df)
        df = calculate_rsi(df)
        df = calculate_lr_slope(df)
        df = calculate_pvi(df)
        # Add CPR calculation if you have pivot points
        # df = calculate_cpr(df)
        return df

    def check_entry(self, row):
        # 4 condition confirmation for bullish and bearish entries
        bullish = (
            row['close'] > row['ma9'] > row['ma20'] > row['ma50'] > row['ma200'] and
            row['rsi'] > row['rsi_ma26'] > row['rsi_ma14'] > row['rsi_ma9'] and
            row['pvi'] > 0 and
            row['lr_slope'] > 0
        )
        bearish = (
            row['close'] < row['ma9'] < row['ma20'] < row['ma50'] < row['ma200'] and
            row['rsi'] < row['rsi_ma26'] < row['rsi_ma14'] < row['rsi_ma9'] and
            row['pvi'] < 0 and
            row['lr_slope'] < 0
        )
        if bullish:
            return "bullish"
        elif bearish:
            return "bearish"
        else:
            return None

    def run(self):
        if self.is_friday_315pm():
            # Force exit all positions
            logger.info("Friday 3:15 PM reached - force exiting all positions")
            for sym in list(self.positions.keys()):
                price = self.api.get_price(sym)
                self.exit_trade(sym, price)
            return

        self.state_manager.reset_daily_count_if_new_day()

        for symbol in self.config["symbols"]:
            # Fetch data and prepare indicators
            df = self.fetch_historical_data(symbol, None, None)  # implement dates as needed
            if df is None or df.empty:
                logger.warning(f"No data for {symbol}")
                continue
            df = self.prepare_indicators(df)
            last_row = df.iloc[-1]

            # Check if already in position
            if symbol in self.positions:
                # Exit condition check (implement your exit logic here)
                # For example, simple 2% stop loss or reversal candle detection
                price = last_row['close']
                if self.should_exit(symbol, price, last_row):
                    self.exit_trade(symbol, price)
                continue

            # Entry condition check
            if self.daily_trade_count >= MAX_DAILY_TRADES:
                logger.info("Max daily trades reached, skipping new entries")
                break
            if len(self.positions) >= MAX_SIMULTANEOUS_TRADES:
                logger.info("Max simultaneous trades reached, skipping new entries")
                break

            signal = self.check_entry(last_row)
            if signal:
                price = last_row['close']
                self.enter_trade(symbol, signal, price)

    def enter_trade(self, symbol, direction, price):
        lot_size = self.config["symbols"][symbol]["lot_size"]
        capital_per_trade = self.capital / MAX_DAILY_TRADES
        quantity = int(capital_per_trade / price / lot_size) * lot_size
        if quantity <= 0:
            logger.warning(f"Calculated zero quantity for {symbol}, skipping trade")
            return
        try:
            self.api.place_order(symbol, direction, quantity)
            self.positions[symbol] = {
                "direction": direction,
                "entry_price": price,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.daily_trade_count += 1
            self.state_manager.state["positions"] = self.positions
            self.state_manager.state["daily_trade_count"] = self.daily_trade_count
            self.state_manager.save_state()
            msg = f"Entered {direction} trade on {symbol} at {price}, qty {quantity}"
            logger.info(msg)
            self.notifier.send_telegram(msg)
        except Exception as e:
            logger.error(f"Error entering trade on {symbol}: {e}")
            self.notifier.send_telegram(f"Error entering trade on {symbol}: {e}")

    def exit_trade(self, symbol, price):
        try:
            self.api.close_position(symbol)
            self.positions.pop(symbol, None)
            self.state_manager.state["positions"] = self.positions
            self.state_manager.save_state()
            msg = f"Exited trade on {symbol} at {price}"
            logger.info(msg)
            self.notifier.send_telegram(msg)
        except Exception as e:
            logger.error(f"Error exiting trade on {symbol}: {e}")
            self.notifier.send_telegram(f"Error exiting trade on {symbol}: {e}")

    def should_exit(self, symbol, price, row):
        pos = self.positions.get(symbol)
        if not pos:
            return False
        # Example exit logic: 2% adverse price move or reversal candle logic
        entry_price = pos["entry_price"]
        if pos["direction"] == "bullish" and price < entry_price * 0.98:
            return True
        if pos["direction"] == "bearish" and price > entry_price * 1.02:
            return True
        # Add reversal candle detection here if implemented
        return False


if __name__ == "__main__":
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    capital = float(os.getenv("CAPITAL", 200000))
    bot = SniperSwingBot(config, capital)
    try:
        while True:
            bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        bot.state_manager.save_state()