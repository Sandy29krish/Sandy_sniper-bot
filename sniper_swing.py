import os
import json
import logging
from datetime import datetime, time
import pytz
from functools import lru_cache
import gc
from utils.kite_api import place_order, exit_order
from utils.notifications import Notifier
from utils.swing_config import SYMBOLS, CAPITAL
from utils.lot_manager import get_swing_strike
from utils.nse_data import get_future_price, get_next_expiry_date
from utils.trade_logger import log_swing_trade
from utils.indicators import get_indicators_15m_30m
from utils.ai_assistant import analyze_trade_signal
from logging.handlers import RotatingFileHandler

STATE_FILE = "sniper_swing_state.json"
MAX_DAILY_TRADES = 3
MAX_SIMULTANEOUS_TRADES = 3

# Logger with memory-efficient configuration
def setup_logger():
    logger = logging.getLogger("SniperSwing")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler("sniper_swing.log", maxBytes=10*1024*1024, backupCount=3)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()

# Optimized State Manager with memory efficiency
class StateManager:
    def __init__(self, filename=STATE_FILE):
        self.filename = filename
        self._state = None
        self._last_loaded = None
        
    @property
    def state(self):
        """Lazy loading of state with caching"""
        current_time = datetime.now().timestamp()
        if self._state is None or (current_time - self._last_loaded) > 60:  # Cache for 1 minute
            self._state = self.load_state()
            self._last_loaded = current_time
        return self._state

    def load_state(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load state: {e}")
        return {"positions": {}, "daily_trade_count": 0, "last_trade_date": None}

    def save(self):
        """Atomic save to prevent corruption"""
        temp_file = f"{self.filename}.tmp"
        try:
            with open(temp_file, "w") as f:
                json.dump(self._state, f, indent=2)
            os.replace(temp_file, self.filename)  # Atomic operation
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def reset_if_new_day(self):
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
        if self.state["last_trade_date"] != today:
            self._state["daily_trade_count"] = 0
            self._state["last_trade_date"] = today
            self.save()

class SniperSwingBot:
    def __init__(self, config, capital):
        self.config = config
        self.capital = capital
        self.notifier = Notifier(config["telegram_token"], config["telegram_id"])
        self.state = StateManager()
        self._cached_prices = {}
        self._cache_timestamp = {}
        
    @lru_cache(maxsize=32)
    def _get_timezone(self):
        """Cache timezone object"""
        return pytz.timezone("Asia/Kolkata")

    def is_friday_315(self):
        now = datetime.now(self._get_timezone())
        return now.weekday() == 4 and now.time() >= time(15, 15)

    def _get_cached_price(self, symbol, cache_duration=30):
        """Get cached price to reduce API calls"""
        current_time = datetime.now().timestamp()
        cache_key = f"{symbol}_price"
        
        if (cache_key in self._cached_prices and 
            cache_key in self._cache_timestamp and
            (current_time - self._cache_timestamp[cache_key]) < cache_duration):
            return self._cached_prices[cache_key]
        
        try:
            price = get_future_price(symbol)
            self._cached_prices[cache_key] = price
            self._cache_timestamp[cache_key] = current_time
            return price
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return self._cached_prices.get(cache_key)  # Return cached value if available

    def run(self):
        try:
            self.state.reset_if_new_day()

            if self.is_friday_315():
                logger.info("Forced exit at 3:15 PM Friday")
                self._exit_all_positions()
                return

            if self.state.state["daily_trade_count"] >= MAX_DAILY_TRADES:
                logger.info("Max daily trades reached")
                return

            # Process existing positions first (more critical)
            self._process_existing_positions()
            
            # Then look for new opportunities
            self._process_new_opportunities()
            
            # Clean up memory periodically
            self._cleanup_memory()
            
        except Exception as e:
            logger.error(f"Error in bot run: {e}")
            raise

    def _exit_all_positions(self):
        """Exit all positions efficiently"""
        positions_to_exit = list(self.state.state["positions"].keys())
        for symbol in positions_to_exit:
            try:
                self.exit_trade(symbol)
            except Exception as e:
                logger.error(f"Failed to exit {symbol}: {e}")

    def _process_existing_positions(self):
        """Process existing positions for exit conditions"""
        positions_to_check = list(self.state.state["positions"].keys())
        for symbol in positions_to_check:
            try:
                if self.should_exit(symbol):
                    self.exit_trade(symbol)
            except Exception as e:
                logger.error(f"Error processing position {symbol}: {e}")

    def _process_new_opportunities(self):
        """Process new trading opportunities"""
        if len(self.state.state["positions"]) >= MAX_SIMULTANEOUS_TRADES:
            logger.info("Max simultaneous positions open")
            return

        for symbol in SYMBOLS:
            if symbol in self.state.state["positions"]:
                continue
                
            if len(self.state.state["positions"]) >= MAX_SIMULTANEOUS_TRADES:
                logger.info("Max simultaneous positions reached during processing")
                break

            try:
                self._evaluate_symbol_entry(symbol)
            except Exception as e:
                logger.error(f"Error evaluating {symbol}: {e}")
                continue

    def _evaluate_symbol_entry(self, symbol):
        """Evaluate entry conditions for a symbol"""
        signal, indicators = get_indicators_15m_30m(symbol)
        if not signal:
            return

        if not self._validate_entry_conditions(indicators):
            return

        # Get market data
        expiry = get_next_expiry_date(symbol)
        future_price = self._get_cached_price(symbol)
        if not future_price:
            logger.warning(f"Could not get price for {symbol}")
            return
            
        strike, premium = get_swing_strike(symbol, future_price, signal, expiry)
        lots = SYMBOLS[symbol]["lot_size"]
        quantity = self.calculate_lot_size(premium, lots)
        
        if quantity == 0:
            logger.warning(f"Lot size 0 for {symbol}, skipping.")
            return

        self._execute_entry_order(symbol, signal, strike, premium, quantity, expiry, indicators)

    def _validate_entry_conditions(self, indicators):
        """Validate all entry conditions efficiently"""
        return (indicators["rsi"] > indicators["rsi_ma26"] and
                indicators["ma_hierarchy"] and
                indicators["pvi_positive"] and
                indicators["lr_slope_positive"])

    def _execute_entry_order(self, symbol, signal, strike, premium, quantity, expiry, indicators):
        """Execute entry order with proper error handling"""
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
            
            # Update state atomically
            self.state.state["positions"][symbol] = {
                "signal": signal,
                "entry_price": premium,
                "strike": strike,
                "expiry": expiry,
                "timestamp": datetime.utcnow().isoformat(),
                "quantity": quantity  # Store quantity for exit
            }
            self.state.state["daily_trade_count"] += 1
            self.state.save()
            
            msg = f"✅ {symbol} SWING {signal.upper()} ENTRY\nStrike: {strike}, Qty: {quantity}, Expiry: {expiry}\n\n🤖 Reason:\n{reasoning}"
            self.notifier.send_telegram(msg)
            log_swing_trade(symbol, signal, strike, premium, quantity, expiry, reasoning)
            
        except Exception as e:
            logger.error(f"Order failed for {symbol}: {e}")
            self.notifier.send_telegram(f"❌ Order failed for {symbol}: {e}")

    def calculate_lot_size(self, premium, lot_size):
        """Optimized lot size calculation"""
        if premium <= 0:
            return 0
        capital_per_trade = self.capital / MAX_DAILY_TRADES
        max_lots = int(capital_per_trade / (premium * lot_size))
        return max(0, max_lots * lot_size)

    def should_exit(self, symbol):
        """Improved exit logic with better price fetching"""
        data = self.state.state["positions"].get(symbol)
        if not data:
            return False
            
        try:
            # Use cached price for efficiency
            current_price = self._get_cached_price(symbol)
            if not current_price:
                logger.warning(f"Could not get current price for {symbol}")
                return False
                
            entry_price = data["entry_price"]
            signal = data["signal"]

            # Stop loss conditions
            if signal == "bullish" and current_price < entry_price * 0.95:
                logger.info(f"Stop loss triggered for {symbol} (bullish)")
                return True
            if signal == "bearish" and current_price > entry_price * 1.05:
                logger.info(f"Stop loss triggered for {symbol} (bearish)")
                return True

            return False
            
        except Exception as e:
            logger.error(f"Error checking exit condition for {symbol}: {e}")
            return False

    def exit_trade(self, symbol):
        """Improved exit trade with better error handling"""
        data = self.state.state["positions"].get(symbol)
        if not data:
            logger.warning(f"No position data found for {symbol}")
            return
            
        try:
            quantity = data.get("quantity", SYMBOLS[symbol]["lot_size"])
            
            exit_order(
                tradingsymbol=data["strike"],
                exchange="NFO",
                quantity=quantity,
                transaction_type="SELL" if data["signal"] == "bullish" else "BUY",
                product="NRML",
                order_type="MARKET"
            )
            
            msg = f"🚪 EXITED {symbol} position"
            self.notifier.send_telegram(msg)
            
            # Remove from state atomically
            self.state.state["positions"].pop(symbol, None)
            self.state.save()
            
        except Exception as e:
            logger.error(f"Exit failed for {symbol}: {e}")
            self.notifier.send_telegram(f"❌ Exit failed for {symbol}: {e}")

    def _cleanup_memory(self):
        """Periodic memory cleanup"""
        # Clear old cached prices (older than 5 minutes)
        current_time = datetime.now().timestamp()
        keys_to_remove = []
        
        for key, timestamp in self._cache_timestamp.items():
            if (current_time - timestamp) > 300:  # 5 minutes
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._cached_prices.pop(key, None)
            self._cache_timestamp.pop(key, None)
        
        # Force garbage collection periodically
        if len(keys_to_remove) > 5:
            gc.collect()

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
