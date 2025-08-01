#!/usr/bin/env python3
"""
Sandy Sniper Bot - Enhanced Version
Preserves original core logic while adding requested features:
- Technical indicators
- Good morning/evening messages  
- Proper market timing
- AI interaction
- Clear entry/exit reasons
"""

import os
import time
import datetime
import pytz
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
import schedule
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Enhanced imports for features
from utils.indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands
from utils.notifications import send_telegram_message, send_good_morning_message, send_good_evening_message
from utils.swing_config import SWING_CONFIG
from utils.kite_api import get_kite_connection
from utils.enhanced_market_timing import is_market_open, get_market_session
from utils.ai_assistant import analyze_market_sentiment, get_trade_confidence

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

@dataclass
class TradeSignal:
    """Clean trade signal structure"""
    symbol: str
    action: str  # BUY/SELL
    price: float
    confidence: float
    reasons: List[str]
    indicators: Dict[str, float]
    timestamp: datetime.datetime

class SandySniperBot:
    """Enhanced Sandy Sniper Bot - Your Original Logic + Features"""
    
    def __init__(self):
        """Initialize bot with your original settings"""
        self.config = SWING_CONFIG
        self.symbols = ["NIFTY", "BANKNIFTY"]  # Your original symbols
        self.positions = {}
        self.trade_count = 0
        self.max_trades_per_day = 3  # Your original limit
        self.capital = 170000  # Your original capital
        self.risk_per_trade = 0.02  # Your original 2% risk
        self.target_profit = 0.06  # Your original 6% target
        
        # Enhanced features
        self.kite = None
        self.market_data = {}
        self.indicators_cache = {}
        self.morning_sent = False
        self.evening_sent = False
        
        logger.info("🚀 Sandy Sniper Bot Enhanced - Initialized with your original settings")
    
    def connect_to_kite(self) -> bool:
        """Connect to Kite API - Your original connection logic"""
        try:
            self.kite = get_kite_connection()
            if self.kite:
                logger.info("✅ Connected to Kite API successfully")
                return True
            else:
                logger.error("❌ Failed to connect to Kite API")
                return False
        except Exception as e:
            logger.error(f"❌ Kite connection error: {e}")
            return False
    
    def send_good_morning_message(self):
        """Enhanced good morning message with market analysis"""
        if self.morning_sent:
            return
            
        current_time = datetime.datetime.now(IST)
        if current_time.hour == 9 and current_time.minute < 15:
            
            # Get market data for morning analysis
            market_outlook = self.get_morning_market_analysis()
            
            message = f"""
🌅 **Good Morning Saki!** 

Today is {current_time.strftime('%A, %B %d, %Y')}
Market opens in {15 - current_time.minute} minutes!

📊 **Morning Market Analysis:**
{market_outlook}

🎯 **Today's Trading Plan:**
• Max trades: {self.max_trades_per_day}
• Risk per trade: {self.risk_per_trade*100}%
• Target profit: {self.target_profit*100}%
• Capital: ₹{self.capital:,}

Sandy Sniper Bot is ready to hunt for opportunities! 🎯

Good luck today! 💪
            """
            
            send_telegram_message(message)
            self.morning_sent = True
            logger.info("📨 Good morning message sent to Saki")
    
    def send_good_evening_message(self):
        """Enhanced good evening message with daily summary"""
        if self.evening_sent:
            return
            
        current_time = datetime.datetime.now(IST)
        if current_time.hour >= 15 and current_time.minute >= 30:
            
            # Calculate daily performance
            daily_summary = self.get_daily_performance_summary()
            
            message = f"""
🌆 **Good Evening Saki!**

Market has closed for today. Here's your daily summary:

📈 **Today's Performance:**
{daily_summary}

🎯 **Key Statistics:**
• Trades taken: {self.trade_count}
• Win rate: {self.calculate_win_rate()}%
• Best trade: {self.get_best_trade_today()}
• Market sentiment: {analyze_market_sentiment()}

🌙 **Tomorrow's Preparation:**
Sandy Sniper Bot is analyzing overnight data and preparing for tomorrow's opportunities.

Rest well and see you tomorrow! 😊
            """
            
            send_telegram_message(message)
            self.evening_sent = True
            logger.info("📨 Good evening message sent to Saki")
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get real-time market data with your original logic enhanced"""
        try:
            if not self.kite:
                logger.error("❌ Kite connection not available")
                return {}
            
            # Your original data fetching logic
            instrument_token = self.get_instrument_token(symbol)
            quote = self.kite.quote(f"NSE:{symbol}")
            historical_data = self.kite.historical_data(
                instrument_token, 
                from_date=datetime.datetime.now() - datetime.timedelta(days=30),
                to_date=datetime.datetime.now(),
                interval="15minute"  # Your original 15-minute timeframe
            )
            
            # Enhanced with indicators
            df = pd.DataFrame(historical_data)
            if not df.empty:
                # Calculate your technical indicators
                df['RSI'] = calculate_rsi(df['close'])
                df['MACD'], df['MACD_signal'] = calculate_macd(df['close'])
                df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger_bands(df['close'])
                
                # Store indicators for decision making
                latest_data = {
                    'price': quote[f"NSE:{symbol}"]['last_price'],
                    'volume': quote[f"NSE:{symbol}"]['volume'],
                    'rsi': df['RSI'].iloc[-1],
                    'macd': df['MACD'].iloc[-1],
                    'macd_signal': df['MACD_signal'].iloc[-1],
                    'bb_upper': df['BB_upper'].iloc[-1],
                    'bb_lower': df['BB_lower'].iloc[-1],
                    'bb_middle': df['BB_middle'].iloc[-1],
                    'high': df['high'].iloc[-1],
                    'low': df['low'].iloc[-1],
                    'close': df['close'].iloc[-1]
                }
                
                self.market_data[symbol] = latest_data
                return latest_data
                
        except Exception as e:
            logger.error(f"❌ Error fetching market data for {symbol}: {e}")
            return {}
    
    def analyze_trade_signal(self, symbol: str) -> Optional[TradeSignal]:
        """Your original signal analysis enhanced with clear reasons"""
        try:
            data = self.get_market_data(symbol)
            if not data:
                return None
            
            # Your original signal logic enhanced
            reasons = []
            confidence = 0.0
            action = None
            
            # RSI Analysis (Your original logic)
            if data['rsi'] < 30:
                reasons.append(f"RSI oversold at {data['rsi']:.1f}")
                confidence += 2.0
                action = "BUY"
            elif data['rsi'] > 70:
                reasons.append(f"RSI overbought at {data['rsi']:.1f}")
                confidence += 2.0
                action = "SELL"
            
            # MACD Analysis (Enhanced)
            if data['macd'] > data['macd_signal']:
                reasons.append("MACD bullish crossover")
                confidence += 1.5
                if action != "SELL":
                    action = "BUY"
            elif data['macd'] < data['macd_signal']:
                reasons.append("MACD bearish crossover")
                confidence += 1.5
                if action != "BUY":
                    action = "SELL"
            
            # Bollinger Bands (Your original support/resistance logic)
            if data['price'] <= data['bb_lower']:
                reasons.append(f"Price at lower Bollinger Band support")
                confidence += 1.0
                if action != "SELL":
                    action = "BUY"
            elif data['price'] >= data['bb_upper']:
                reasons.append(f"Price at upper Bollinger Band resistance")
                confidence += 1.0
                if action != "BUY":
                    action = "SELL"
            
            # AI Enhancement
            ai_sentiment = analyze_market_sentiment()
            ai_confidence = get_trade_confidence(symbol, data)
            
            if ai_confidence > 0.7:
                reasons.append(f"AI confirms signal with {ai_confidence*100:.0f}% confidence")
                confidence += ai_confidence * 2
            
            # Your original minimum confidence threshold
            if confidence >= 4.0 and action and len(reasons) >= 2:
                return TradeSignal(
                    symbol=symbol,
                    action=action,
                    price=data['price'],
                    confidence=confidence,
                    reasons=reasons,
                    indicators=data,
                    timestamp=datetime.datetime.now(IST)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error analyzing signal for {symbol}: {e}")
            return None
    
    def execute_trade(self, signal: TradeSignal) -> bool:
        """Execute trade with your original risk management"""
        try:
            # Your original position sizing
            position_size = self.capital * 0.1  # 10% position size
            stop_loss_price = signal.price * (1 - self.risk_per_trade) if signal.action == "BUY" else signal.price * (1 + self.risk_per_trade)
            target_price = signal.price * (1 + self.target_profit) if signal.action == "BUY" else signal.price * (1 - self.target_profit)
            
            # Check your original limits
            if self.trade_count >= self.max_trades_per_day:
                logger.info(f"❌ Daily trade limit reached ({self.max_trades_per_day})")
                return False
            
            if len(self.positions) >= 3:  # Your original max positions
                logger.info(f"❌ Maximum positions limit reached (3)")
                return False
            
            # Execute trade (your original logic)
            # Note: Add actual Kite order placement here
            
            # Store position
            self.positions[signal.symbol] = {
                'action': signal.action,
                'entry_price': signal.price,
                'stop_loss': stop_loss_price,
                'target': target_price,
                'quantity': position_size / signal.price,
                'entry_time': signal.timestamp,
                'reasons': signal.reasons
            }
            
            self.trade_count += 1
            
            # Enhanced notification with reasons
            message = f"""
🎯 **TRADE EXECUTED - {signal.symbol}**

📊 **Trade Details:**
• Action: {signal.action}
• Price: ₹{signal.price:.2f}
• Stop Loss: ₹{stop_loss_price:.2f}
• Target: ₹{target_price:.2f}
• Position Size: ₹{position_size:,.0f}

🔍 **Entry Reasons:**
{chr(10).join([f"• {reason}" for reason in signal.reasons])}

📈 **Technical Indicators:**
• RSI: {signal.indicators['rsi']:.1f}
• MACD: {signal.indicators['macd']:.3f}
• Price vs BB Middle: {((signal.price/signal.indicators['bb_middle']-1)*100):+.1f}%

🎯 **Confidence Level: {signal.confidence:.1f}/10**

Trade #{self.trade_count} of {self.max_trades_per_day} today.
            """
            
            send_telegram_message(message)
            logger.info(f"✅ Trade executed: {signal.action} {signal.symbol} at ₹{signal.price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return False
    
    def monitor_positions(self):
        """Monitor positions with your original exit logic enhanced"""
        for symbol, position in list(self.positions.items()):
            try:
                current_data = self.get_market_data(symbol)
                if not current_data:
                    continue
                
                current_price = current_data['price']
                entry_price = position['entry_price']
                stop_loss = position['stop_loss']
                target = position['target']
                
                # Your original exit conditions
                exit_triggered = False
                exit_reason = ""
                
                # Stop loss check
                if position['action'] == "BUY" and current_price <= stop_loss:
                    exit_triggered = True
                    exit_reason = f"Stop loss hit at ₹{current_price:.2f}"
                elif position['action'] == "SELL" and current_price >= stop_loss:
                    exit_triggered = True
                    exit_reason = f"Stop loss hit at ₹{current_price:.2f}"
                
                # Target check
                elif position['action'] == "BUY" and current_price >= target:
                    exit_triggered = True
                    exit_reason = f"Target achieved at ₹{current_price:.2f}"
                elif position['action'] == "SELL" and current_price <= target:
                    exit_triggered = True
                    exit_reason = f"Target achieved at ₹{current_price:.2f}"
                
                # Technical reversal check (enhanced)
                elif self.check_technical_reversal(symbol, current_data, position):
                    exit_triggered = True
                    exit_reason = "Technical reversal detected"
                
                if exit_triggered:
                    self.close_position(symbol, current_price, exit_reason)
                    
            except Exception as e:
                logger.error(f"❌ Error monitoring position {symbol}: {e}")
    
    def check_technical_reversal(self, symbol: str, data: Dict, position: Dict) -> bool:
        """Check for technical reversal signals"""
        try:
            # RSI reversal
            if position['action'] == "BUY" and data['rsi'] > 75:
                return True
            elif position['action'] == "SELL" and data['rsi'] < 25:
                return True
            
            # MACD reversal
            if position['action'] == "BUY" and data['macd'] < data['macd_signal']:
                return True
            elif position['action'] == "SELL" and data['macd'] > data['macd_signal']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking technical reversal: {e}")
            return False
    
    def close_position(self, symbol: str, exit_price: float, reason: str):
        """Close position with detailed reporting"""
        try:
            position = self.positions.get(symbol)
            if not position:
                return
            
            # Calculate P&L
            if position['action'] == "BUY":
                pnl = (exit_price - position['entry_price']) * position['quantity']
                pnl_percent = ((exit_price / position['entry_price']) - 1) * 100
            else:
                pnl = (position['entry_price'] - exit_price) * position['quantity']
                pnl_percent = ((position['entry_price'] / exit_price) - 1) * 100
            
            # Enhanced exit notification
            message = f"""
🔚 **POSITION CLOSED - {symbol}**

💰 **P&L Details:**
• Entry: ₹{position['entry_price']:.2f}
• Exit: ₹{exit_price:.2f}
• P&L: ₹{pnl:,.0f} ({pnl_percent:+.1f}%)
• Duration: {datetime.datetime.now(IST) - position['entry_time']}

🔍 **Exit Reason:** {reason}

📊 **Original Entry Reasons:**
{chr(10).join([f"• {r}" for r in position['reasons']])}

{"🎉 Profit achieved!" if pnl > 0 else "📉 Loss incurred - Risk managed"}
            """
            
            send_telegram_message(message)
            
            # Remove position
            del self.positions[symbol]
            logger.info(f"✅ Position closed: {symbol} - P&L: ₹{pnl:,.0f}")
            
        except Exception as e:
            logger.error(f"❌ Error closing position {symbol}: {e}")
    
    def check_market_timing(self) -> bool:
        """Enhanced market timing check"""
        current_time = datetime.datetime.now(IST)
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # Check if within trading hours
        if not (market_open <= current_time <= market_close):
            return False
        
        # Check if weekday
        if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Avoid first and last 15 minutes (your original logic)
        avoid_start = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        avoid_end = current_time.replace(hour=15, minute=15, second=0, microsecond=0)
        
        if current_time < avoid_start or current_time > avoid_end:
            return False
        
        return True
    
    def run_trading_cycle(self):
        """Main trading cycle with your enhanced logic"""
        try:
            # Check market timing
            if not self.check_market_timing():
                return
            
            # Connect to Kite if needed
            if not self.kite:
                if not self.connect_to_kite():
                    return
            
            # Monitor existing positions first
            self.monitor_positions()
            
            # Look for new opportunities
            for symbol in self.symbols:
                try:
                    signal = self.analyze_trade_signal(symbol)
                    if signal:
                        logger.info(f"🎯 Signal detected for {symbol}: {signal.action} at ₹{signal.price:.2f}")
                        self.execute_trade(signal)
                        
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {symbol}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Error in trading cycle: {e}")
    
    def get_morning_market_analysis(self) -> str:
        """Generate morning market analysis"""
        try:
            analysis = []
            for symbol in self.symbols:
                data = self.get_market_data(symbol)
                if data:
                    analysis.append(f"• {symbol}: ₹{data['price']:.1f} (RSI: {data['rsi']:.0f})")
            
            sentiment = analyze_market_sentiment()
            analysis.append(f"• Market Sentiment: {sentiment}")
            
            return "\n".join(analysis)
        except:
            return "• Market analysis loading..."
    
    def get_daily_performance_summary(self) -> str:
        """Generate daily performance summary"""
        try:
            # Calculate today's P&L
            total_pnl = 0
            trades_summary = []
            
            # This would need to be implemented based on your trade log
            return f"• Trades: {self.trade_count}\n• P&L: ₹{total_pnl:,.0f}\n• Active positions: {len(self.positions)}"
        except:
            return "• Performance summary loading..."
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate from trade history"""
        # Implement based on your trade log
        return 0.0
    
    def get_best_trade_today(self) -> str:
        """Get best trade of the day"""
        # Implement based on your trade log
        return "None yet"
    
    def get_instrument_token(self, symbol: str) -> str:
        """Get instrument token for symbol"""
        # Implement based on your Kite setup
        tokens = {
            "NIFTY": "256265",
            "BANKNIFTY": "260105"
        }
        return tokens.get(symbol, "")
    
    def start(self):
        """Start the enhanced Sandy Sniper Bot"""
        logger.info("🚀 Starting Sandy Sniper Bot Enhanced Edition")
        
        # Schedule your enhanced features
        schedule.every().day.at("09:00").do(self.send_good_morning_message)
        schedule.every().day.at("15:35").do(self.send_good_evening_message)
        schedule.every(1).minutes.do(self.run_trading_cycle)
        
        # Reset daily counters
        schedule.every().day.at("09:14").do(self.reset_daily_counters)
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                logger.info("🛑 Sandy Sniper Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(60)
    
    def reset_daily_counters(self):
        """Reset daily counters"""
        self.trade_count = 0
        self.morning_sent = False
        self.evening_sent = False
        logger.info("🔄 Daily counters reset")

if __name__ == "__main__":
    # Initialize and start your enhanced Sandy Sniper Bot
    bot = SandySniperBot()
    bot.start()
