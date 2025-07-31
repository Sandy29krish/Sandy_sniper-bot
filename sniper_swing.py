import os
import json
import logging
from datetime import datetime, time
import pytz
from functools import lru_cache
import gc
from utils.kite_api import get_kite_instance, get_live_price, place_order, get_positions
from utils.notifications import Notifier
from utils.swing_config import SYMBOLS, CAPITAL, RISK_CONFIG
from utils.lot_manager import get_swing_strike
from utils.nse_data import get_future_price, get_next_expiry_date
from utils.trade_logger import log_swing_trade
from utils.indicators import get_indicators_15m_30m
from utils.ai_assistant import analyze_trade_signal, analyze_exit_signal
from logging.handlers import RotatingFileHandler
from market_timing import is_market_open, get_market_status, is_friday_315, is_within_first_15_minutes
from utils.advanced_exit_manager import AdvancedExitManager
from utils.nse_option_chain import nse_option_chain, get_current_expiry, get_next_expiry
from utils.auto_rollover_manager import auto_rollover_manager, check_and_process_rollovers
from utils.signal_strength_analyzer import signal_strength_analyzer, rank_trading_signals
from utils.gap_handler import gap_handler, detect_and_handle_gaps, monitor_gap_affected_positions
from utils.intelligent_order_manager import intelligent_order_manager, execute_smart_order
from utils.enhanced_scheduler import enhanced_scheduler, is_trading_time
from utils.intelligent_watchdog import start_watchdog_monitoring, get_watchdog_health_report

STATE_FILE = "sniper_swing_state.json"
MAX_DAILY_TRADES = RISK_CONFIG['max_daily_trades']
MAX_SIMULTANEOUS_TRADES = RISK_CONFIG['max_simultaneous_trades']

# SINGLE KITE SESSION - Global reference for efficiency
_single_kite = None

def get_single_kite_session():
    """Get the single Kite session for ALL operations"""
    global _single_kite
    if _single_kite is None:
        _single_kite = get_kite_instance()
    return _single_kite

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
        import os
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_id = os.getenv("TELEGRAM_ID")
        self.notifier = Notifier(telegram_token, telegram_id)
        self.state = StateManager()
        self._cached_prices = {}
        self._cache_timestamp = {}
        self.advanced_exit_manager = AdvancedExitManager()
        
        # Start intelligent watchdog protection
        logger.info("🐕‍🦺 Initializing Intelligent Watchdog Protection...")
        start_watchdog_monitoring(notification_callback=self.notifier.send_telegram)
        
        # Start enhanced scheduler
        logger.info("⏰ Initializing Enhanced Scheduler...")
        enhanced_scheduler.set_bot_instance(self, notification_callback=self.notifier.send_telegram)
        enhanced_scheduler.start_enhanced_scheduler()
        
        logger.info("🚀 Sniper Swing Bot fully initialized with intelligent protection!")
        
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
            # Check if bot should be active based on enhanced schedule
            if not is_trading_time():
                logger.info("😴 Bot in sleep mode - outside trading hours")
                return
                
            # Check market status first
            market_status = get_market_status()
            logger.info(f"📊 {market_status['status']} - {market_status['message']}")
            
            # Only trade when market is open
            if not is_market_open():
                logger.info("🏛️ Market is closed. Skipping trading cycle.")
                return
                
            self.state.reset_if_new_day()

            if is_friday_315():
                logger.info("🕒 Forced exit at 3:15 PM Friday")
                self._exit_all_positions_intelligent()
                return

            if self.state.state["daily_trade_count"] >= MAX_DAILY_TRADES:
                logger.info("📈 Max daily trades reached")
                return

            # 1. PRIORITY: Handle gap scenarios immediately
            logger.info("🔍 Checking for gap scenarios...")
            updated_positions = detect_and_handle_gaps(self.state.state["positions"])
            if updated_positions != self.state.state["positions"]:
                self.state.state["positions"] = updated_positions
                self.state.save()
                logger.info("✅ Gap scenarios processed")

            # 2. Process existing positions (exits, rollovers) - ALWAYS do this
            self._process_existing_positions()
            
            # 3. Check auto rollovers (1 week buffer)
            logger.info("🔄 Checking for auto rollovers...")
            rollover_updated_positions = check_and_process_rollovers(self.state.state["positions"])
            if rollover_updated_positions != self.state.state["positions"]:
                self.state.state["positions"] = rollover_updated_positions
                self.state.save()
                logger.info("✅ Auto rollovers processed")
            
            # 4. Monitor gap-affected positions
            gap_monitored_positions = monitor_gap_affected_positions(self.state.state["positions"])
            if gap_monitored_positions != self.state.state["positions"]:
                self.state.state["positions"] = gap_monitored_positions
                self.state.save()
            
            # Check if we're in the first 15 minutes of market open
            if is_within_first_15_minutes():
                logger.info("⚡ In first 15 minutes - monitoring existing positions only, skipping new entries due to volatility.")
                return
            
            # 5. Look for new opportunities with signal strength ranking
            self._process_new_opportunities_with_strength_ranking()
            
            # Clean up memory periodically
            self._cleanup_memory()
            
        except Exception as e:
            logger.error(f"Error in bot run: {e}")
            raise

    def _exit_all_positions_intelligent(self):
        """Exit all positions using intelligent order management"""
        positions_to_exit = list(self.state.state["positions"].keys())
        for symbol in positions_to_exit:
            try:
                self.exit_trade_intelligent(symbol, scenario='friday_315')
            except Exception as e:
                logger.error(f"Failed to exit {symbol}: {e}")

    def _process_existing_positions(self):
        """Process existing positions for user's exact exit conditions"""
        positions_to_check = list(self.state.state["positions"].keys())
        for symbol in positions_to_check:
            try:
                should_exit, exit_reason = self.should_exit(symbol)
                if should_exit:
                    self.exit_trade(symbol, exit_reason or "Exit condition triggered")
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

    def _process_new_opportunities_with_strength_ranking(self):
        """Look for new trading opportunities with signal strength ranking"""
        current_positions = len(self.state.state["positions"])
        if current_positions >= MAX_SIMULTANEOUS_TRADES:
            logger.info(f"📊 Max positions reached ({current_positions}/{MAX_SIMULTANEOUS_TRADES})")
            return
            
        # Collect all signal candidates
        signal_candidates = []
        
        for symbol in SYMBOLS:
            if symbol in self.state.state["positions"]:
                continue  # Already have position
                
            # Get signal and indicators
            signal, indicators = get_indicators_15m_30m(symbol)
            if signal and indicators:
                candidate = {
                    'symbol': symbol,
                    'signal_type': signal,
                    'indicators': indicators
                }
                signal_candidates.append(candidate)
        
        if not signal_candidates:
            logger.info("📊 No signal candidates found")
            return
        
        # Rank signals by strength (only Strong, Very Strong, Super Strong)
        logger.info(f"🎯 Analyzing {len(signal_candidates)} signal candidates...")
        ranked_signals = rank_trading_signals(signal_candidates)
        
        if not ranked_signals:
            logger.info("📊 No signals meet minimum strength threshold (7.0+)")
            return
        
        logger.info(f"🏆 Found {len(ranked_signals)} strong signals")
        
        # Execute trades based on ranking (strongest first)
        positions_to_take = min(len(ranked_signals), MAX_SIMULTANEOUS_TRADES - current_positions)
        
        for i, signal_data in enumerate(ranked_signals[:positions_to_take]):
            symbol = signal_data['symbol']
            signal_type = signal_data['signal_type']
            strength = signal_data['total_strength']
            grade = signal_data['strength_grade']
            
            logger.info(f"🎯 Executing {grade} signal for {symbol} (Strength: {strength:.2f})")
            
            # Execute the trade using existing method but with strength info
            self._evaluate_symbol_entry_with_strength(symbol, signal_data)
            
        logger.info(f"✅ Processed {positions_to_take} ranked signals")

    def _evaluate_symbol_entry_with_strength(self, symbol, signal_data):
        """Evaluate entry with strength data"""
        try:
            signal_type = signal_data['signal_type']
            indicators = signal_data['indicators']
            strength = signal_data['total_strength']
            
            if not self._validate_entry_conditions(indicators):
                return

            # Get market data with NSE integration
            current_expiry = get_current_expiry(symbol)
            if not current_expiry:
                current_expiry = get_next_expiry_date(symbol)  # Fallback
                
            future_price = self._get_cached_price(symbol)
            if not future_price:
                logger.warning(f"Could not get price for {symbol}")
                return
                
            strike, premium = get_swing_strike(symbol, future_price, signal_type, current_expiry)
            lots = SYMBOLS[symbol]["lot_size"]
            quantity = self.calculate_lot_size(premium, lots)
            
            if quantity == 0:
                logger.warning(f"Lot size 0 for {symbol}, skipping.")
                return

            # Execute with strength info
            self._execute_entry_order_with_strength(symbol, signal_type, strike, premium, quantity, current_expiry, indicators, strength)
            
        except Exception as e:
            logger.error(f"Error in strength-based entry for {symbol}: {e}")

    def _execute_entry_order_with_strength(self, symbol, signal, strike, premium, quantity, expiry, indicators, strength):
        """Execute entry order with intelligent order management"""
        reasoning = analyze_trade_signal(symbol, indicators, signal)
        strength_info = f"Signal Strength: {strength:.2f}/10"

        try:
            # Use intelligent order manager for entry
            success = execute_smart_order(
                tradingsymbol=strike,
                exchange="NFO",
                quantity=quantity,
                transaction_type="BUY" if signal == "bullish" else "SELL",
                scenario='normal_entry',
                symbol=symbol,
                current_premium=premium,
                signal_strength=strength
            )
            
            if success:
                # Update state with strength info
                self.state.state["positions"][symbol] = {
                    "signal": signal,
                    "entry_price": premium,
                    "strike": strike,
                    "expiry": expiry,
                    "timestamp": datetime.utcnow().isoformat(),
                    "quantity": quantity,
                    "indicators": indicators,
                    "signal_strength": strength,  # Add strength tracking
                    "original_quantity": quantity  # For partial exits
                }
                self.state.state["daily_trade_count"] += 1
                self.state.save()
                
                msg = f"✅ {symbol} SWING {signal.upper()} ENTRY\n"
                msg += f"Strike: {strike}, Qty: {quantity}, Expiry: {expiry}\n"
                msg += f"🎯 {strength_info}\n\n🤖 AI Reason:\n{reasoning}"
                
                self.notifier.send_telegram(msg)
                log_swing_trade(symbol, signal, strike, premium, quantity, expiry, f"{reasoning}\n{strength_info}")
                
        except Exception as e:
            logger.error(f"Order failed for {symbol}: {e}")
            self.notifier.send_telegram(f"❌ Order failed for {symbol}: {e}")

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
        """Execute entry order with proper error handling and AI learning"""
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
                "quantity": quantity,  # Store quantity for exit
                "indicators": indicators  # Store indicators for AI learning
            }
            self.state.state["daily_trade_count"] += 1
            self.state.save()
            
            msg = f"✅ {symbol} SWING {signal.upper()} ENTRY\nStrike: {strike}, Qty: {quantity}, Expiry: {expiry}\n\n🤖 AI Reason:\n{reasoning}"
            self.notifier.send_telegram(msg)
            log_swing_trade(symbol, signal, strike, premium, quantity, expiry, reasoning)
            
        except Exception as e:
            logger.error(f"Order failed for {symbol}: {e}")
            self.notifier.send_telegram(f"❌ Order failed for {symbol}: {e}")

    def calculate_lot_size(self, premium, lot_size):
        """
        Dynamic position sizing based on available capital and premium
        lot_size = shares per lot (e.g., NIFTY = 75 shares per lot)
        Calculates maximum affordable lots within capital limits
        """
        if premium <= 0:
            return 0
        
        # Available capital per trade (33% of total capital)
        capital_per_trade = self.capital / MAX_DAILY_TRADES
        
        # Calculate cost per lot
        cost_per_lot = premium * lot_size
        
        # Calculate maximum affordable lots
        max_affordable_lots = int(capital_per_trade / cost_per_lot)
        
        # Ensure we trade at least 1 lot if affordable, max 5 lots for risk management
        if max_affordable_lots >= 1:
            lots_to_trade = min(max_affordable_lots, 5)  # Cap at 5 lots maximum
        else:
            logger.warning(f"⚠️ Cannot afford even 1 lot. Cost: ₹{cost_per_lot}, Available: ₹{capital_per_trade}")
            return 0
        
        # Calculate final quantity
        total_quantity = lots_to_trade * lot_size
        total_cost = premium * total_quantity
        
        logger.info(f"📊 Dynamic Sizing: {lots_to_trade} lot(s) = {total_quantity} qty at ₹{premium} = ₹{total_cost}")
        logger.info(f"💰 Capital utilization: {(total_cost/capital_per_trade)*100:.1f}% of available ₹{capital_per_trade}")
        return total_quantity

    def should_exit(self, symbol):
        """USER'S EXACT EXIT CONDITIONS: 15min SMA cross, volume drop, LR slope, swing highs, AI momentum"""
        data = self.state.state["positions"].get(symbol)
        if not data:
            return False, None
            
        try:
            # Check user's exact exit conditions
            should_exit, exit_reason, exit_type, exit_quantity = self.advanced_exit_manager.check_all_exit_conditions(symbol, data)
            
            if should_exit:
                logger.info(f"🚪 Exit condition triggered for {symbol}: {exit_reason}")
                
                # Handle partial exits (swing highs)
                if exit_type == "partial_profit":
                    self._execute_partial_exit(symbol, exit_quantity, exit_reason)
                    return False, None  # Continue monitoring remaining position
                else:
                    # Full exit required (SMA cross, volume drop, LR slope, AI weakness)
                    return True, exit_reason
            
            # No exit conditions met - continue monitoring
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking exit condition for {symbol}: {e}")
            return False, None
    
    def _execute_partial_exit(self, symbol, exit_quantity, exit_reason):
        """Execute partial exit using intelligent order management"""
        try:
            position_data = self.state.state["positions"].get(symbol)
            if not position_data:
                return
            
            strike = position_data["strike"]
            signal = position_data["signal"]
            entry_price = position_data.get("entry_price", 0)
            signal_strength = position_data.get("signal_strength", 0)
            
            # Get current premium
            current_premium = self._get_cached_price(symbol)
            if not current_premium:
                current_premium = entry_price
            
            # Use intelligent order manager for partial exit
            success = execute_smart_order(
                tradingsymbol=strike,
                exchange="NFO",
                quantity=exit_quantity,
                transaction_type="SELL" if signal == "bullish" else "BUY",
                scenario='profit_booking',
                symbol=symbol,
                current_premium=current_premium,
                signal_strength=signal_strength
            )
            
            if success:
                # Update position data
                updated_position = self.advanced_exit_manager.update_partial_exit_record(
                    position_data, 
                    {'level': 'partial', 'quantity': exit_quantity, 'profit_pct': 0}
                )
                
                self.state.state["positions"][symbol] = updated_position
                self.state.save()
                
                # Send notification
                remaining_qty = updated_position.get('quantity', 0)
                msg = f"📈 {symbol} PARTIAL EXIT\n"
                msg += f"Reason: {exit_reason}\n"
                msg += f"Exited Qty: {exit_quantity}\n"
                msg += f"Remaining Qty: {remaining_qty}\n"
                msg += f"Strike: {strike}"
                
                self.notifier.send_telegram(msg)
                logger.info(f"✅ Partial exit executed for {symbol}: {exit_quantity} units")
                
        except Exception as e:
            logger.error(f"❌ Failed to execute partial exit for {symbol}: {e}")
            self.notifier.send_telegram(f"❌ Partial exit failed for {symbol}: {e}")

    def exit_trade_intelligent(self, symbol, scenario='normal_exit'):
        """Exit trade using intelligent order management"""
        try:
            data = self.state.state["positions"].get(symbol)
            if not data:
                logger.warning(f"No position data for {symbol}")
                return

            strike = data["strike"]
            quantity = data["quantity"]
            signal = data["signal"]
            entry_price = data.get("entry_price", 0)
            signal_strength = data.get("signal_strength", 0)

            # Get current premium for intelligent decision
            current_premium = self._get_cached_price(symbol)
            if not current_premium:
                current_premium = entry_price  # Fallback

            # Use intelligent order manager
            success = execute_smart_order(
                tradingsymbol=strike,
                exchange="NFO",
                quantity=quantity,
                transaction_type="SELL" if signal == "bullish" else "BUY",
                scenario=scenario,
                symbol=symbol,
                current_premium=current_premium,
                signal_strength=signal_strength
            )

            if success:
                # Calculate P&L
                if signal == "bullish":
                    pnl = (current_premium - entry_price) * quantity
                else:
                    pnl = (entry_price - current_premium) * quantity

                pnl_pct = (pnl / (entry_price * quantity)) * 100

                # Remove from positions
                del self.state.state["positions"][symbol]
                self.state.save()

                # Send notification with P&L
                pnl_emoji = "💚" if pnl > 0 else "❤️"
                msg = f"🔚 {symbol} POSITION CLOSED\n"
                msg += f"Entry: ₹{entry_price}, Exit: ₹{current_premium}\n"
                msg += f"{pnl_emoji} P&L: ₹{pnl:.0f} ({pnl_pct:+.1f}%)\n"
                msg += f"Scenario: {scenario}"

                self.notifier.send_telegram(msg)
                logger.info(f"✅ Position closed: {symbol} - P&L: ₹{pnl:.0f}")

        except Exception as e:
            logger.error(f"Error in intelligent exit for {symbol}: {e}")

    def exit_trade(self, symbol, exit_reason="Manual exit"):
        """Enhanced exit trade with mandatory detailed reasoning"""
        data = self.state.state["positions"].get(symbol)
        if not data:
            logger.warning(f"No position data found for {symbol}")
            return
            
        try:
            quantity = data.get("quantity", SYMBOLS[symbol]["lot_size"])
            current_price = self._get_cached_price(symbol)
            
            # Mandatory exit reasoning before executing trade
            exit_reasoning = analyze_exit_signal(symbol, data, exit_reason, current_price)
            logger.info(f"🚪 EXIT ANALYSIS:\n{exit_reasoning}")
            
            exit_order(
                tradingsymbol=data["strike"],
                exchange="NFO",
                quantity=quantity,
                transaction_type="SELL" if data["signal"] == "bullish" else "BUY",
                product="NRML",
                order_type="MARKET"
            )
            
            # Calculate P&L for AI learning
            entry_price = data["entry_price"]
            if current_price and entry_price:
                if data["signal"] == "bullish":
                    profit = (current_price - entry_price) * quantity
                else:
                    profit = (entry_price - current_price) * quantity
                
                # Update AI with trade result
                from utils.ai_assistant import AIAssistant
                ai = AIAssistant()
                trade_result = {
                    "symbol": symbol,
                    "signal": data["signal"],
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "profit": profit,
                    "success": profit > 0,
                    "indicators": data.get("indicators", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
                ai.update_knowledge(trade_result)
                
                # Enhanced notification with detailed reasoning
                profit_pct = (profit / (entry_price * quantity)) * 100
                pnl_emoji = "💚" if profit > 0 else "❤️"
                
                msg = f"🔚 {symbol} POSITION CLOSED\n"
                msg += f"📊 Entry: ₹{entry_price}, Exit: ₹{current_price}\n"
                msg += f"{pnl_emoji} P&L: ₹{profit:.0f} ({profit_pct:+.1f}%)\n"
                msg += f"🎯 Reason: {exit_reason}\n"
                msg += f"\n📋 DETAILED ANALYSIS:\n{exit_reasoning}"
            else:
                msg = f"🔚 {symbol} POSITION CLOSED\n🎯 Reason: {exit_reason}"
            
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
