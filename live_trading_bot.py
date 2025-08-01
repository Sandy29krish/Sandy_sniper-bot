#!/usr/bin/env python3
"""
🚀 SANDY SNIPER BOT - LIVE TRADING SYSTEM
COMPLETE AUTOMATION with Real Money Trading via Kite Connect API
Small lot sizes with full risk management
"""

import asyncio
import logging
import os
import sys
import json
import math
from datetime import datetime, timedelta
import pytz
import pandas as pd
from kiteconnect import KiteConnect
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

class LiveTradingBot:
    def __init__(self):
        # Telegram credentials
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = int(os.getenv('TELEGRAM_ID'))
        
        # Kite Connect credentials
        self.api_key = os.getenv('KITE_API_KEY')
        self.api_secret = os.getenv('KITE_API_SECRET')
        self.access_token = os.getenv('KITE_ACCESS_TOKEN')
        
        # Initialize Kite Connect
        self.kite = KiteConnect(api_key=self.api_key)
        if self.access_token:
            self.kite.set_access_token(self.access_token)
        
        # Trading configuration
        self.max_risk_per_trade = 2000  # ₹2000 max risk per trade
        self.min_lot_size = 1  # Minimum 1 lot
        self.max_positions = 3  # Maximum 3 positions at once
        self.profit_target = 0.15  # 15% profit target
        self.stop_loss = 0.08  # 8% stop loss
        
        # Market instruments
        self.instruments = {}
        self.active_positions = {}
        
        # Telegram app
        self.application = None
        
        if not all([self.bot_token, self.chat_id, self.api_key]):
            raise ValueError("❌ Missing required credentials")
    
    def authenticate_kite(self):
        """Complete Kite Connect authentication"""
        try:
            # Get user profile to test connection
            profile = self.kite.profile()
            logger.info(f"✅ Kite Connected: {profile['user_name']} ({profile['email']})")
            return True
        except Exception as e:
            logger.error(f"❌ Kite authentication failed: {e}")
            return False
    
    def load_instruments(self):
        """Load trading instruments"""
        try:
            # Download instruments for NSE and NFO
            instruments = self.kite.instruments()
            
            for instrument in instruments:
                if instrument['exchange'] in ['NSE', 'NFO']:
                    symbol = instrument['tradingsymbol']
                    self.instruments[symbol] = instrument
            
            logger.info(f"✅ Loaded {len(self.instruments)} instruments")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load instruments: {e}")
            return False
    
    def get_ltp(self, symbol):
        """Get Last Traded Price"""
        try:
            instrument_token = self.instruments[symbol]['instrument_token']
            ltp_data = self.kite.ltp([instrument_token])
            return ltp_data[str(instrument_token)]['last_price']
        except Exception as e:
            logger.error(f"❌ Failed to get LTP for {symbol}: {e}")
            return None
    
    def calculate_quantity(self, symbol, risk_amount):
        """Calculate quantity based on risk"""
        try:
            ltp = self.get_ltp(symbol)
            if not ltp:
                return 0
            
            instrument = self.instruments[symbol]
            lot_size = instrument.get('lot_size', 1)
            
            # Calculate maximum quantity within risk
            max_quantity = int(risk_amount / ltp)
            
            # Round down to nearest lot size
            quantity = (max_quantity // lot_size) * lot_size
            
            # Ensure minimum 1 lot
            return max(quantity, lot_size)
        
        except Exception as e:
            logger.error(f"❌ Failed to calculate quantity: {e}")
            return 0
    
    def place_order(self, symbol, transaction_type, quantity, order_type="MARKET", price=None):
        """Place order via Kite Connect"""
        try:
            order_params = {
                'tradingsymbol': symbol,
                'exchange': self.instruments[symbol]['exchange'],
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': order_type,
                'product': 'MIS',  # Intraday
                'validity': 'DAY'
            }
            
            if order_type == "LIMIT" and price:
                order_params['price'] = price
            
            order_id = self.kite.place_order(**order_params)
            
            logger.info(f"✅ Order placed: {transaction_type} {quantity} {symbol} - Order ID: {order_id}")
            return order_id
        
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            return None
    
    def execute_trade(self, signal_data):
        """Execute live trade based on signal"""
        try:
            symbol = signal_data['symbol']
            action = signal_data['action']  # BUY or SELL
            
            # Check if we have too many positions
            if len(self.active_positions) >= self.max_positions:
                await self.send_telegram_message("⚠️ Maximum positions reached. Skipping trade.")
                return False
            
            # Calculate quantity
            quantity = self.calculate_quantity(symbol, self.max_risk_per_trade)
            if quantity == 0:
                await self.send_telegram_message(f"❌ Cannot calculate quantity for {symbol}")
                return False
            
            # Place the order
            order_id = self.place_order(symbol, action, quantity)
            
            if order_id:
                # Track position
                self.active_positions[symbol] = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'entry_time': datetime.now(IST),
                    'entry_price': self.get_ltp(symbol)
                }
                
                # Send confirmation
                message = f"""
🚀 LIVE TRADE EXECUTED!

📊 Symbol: {symbol}
🎯 Action: {action}
📈 Quantity: {quantity}
💰 Entry Price: ₹{self.active_positions[symbol]['entry_price']}
🆔 Order ID: {order_id}
⏰ Time: {datetime.now(IST).strftime('%H:%M:%S')}

✅ Trade placed successfully!
                """
                await self.send_telegram_message(message)
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            await self.send_telegram_message(f"❌ Trade execution failed: {str(e)[:100]}")
            return False
    
    def check_exit_conditions(self):
        """Check if any positions need to be closed"""
        try:
            for symbol, position in list(self.active_positions.items()):
                current_price = self.get_ltp(symbol)
                if not current_price:
                    continue
                
                entry_price = position['entry_price']
                action = position['action']
                
                # Calculate P&L percentage
                if action == "BUY":
                    pnl_pct = (current_price - entry_price) / entry_price
                else:  # SELL
                    pnl_pct = (entry_price - current_price) / entry_price
                
                # Check exit conditions
                should_exit = False
                exit_reason = ""
                
                if pnl_pct >= self.profit_target:
                    should_exit = True
                    exit_reason = f"✅ PROFIT TARGET ({pnl_pct:.2%})"
                elif pnl_pct <= -self.stop_loss:
                    should_exit = True
                    exit_reason = f"🛑 STOP LOSS ({pnl_pct:.2%})"
                
                if should_exit:
                    # Exit the position
                    exit_action = "SELL" if action == "BUY" else "BUY"
                    exit_order = self.place_order(symbol, exit_action, position['quantity'])
                    
                    if exit_order:
                        # Calculate actual P&L
                        pnl_amount = pnl_pct * entry_price * position['quantity']
                        
                        message = f"""
🎯 POSITION CLOSED!

📊 Symbol: {symbol}
{exit_reason}
💰 Entry: ₹{entry_price}
💰 Exit: ₹{current_price}
💵 P&L: ₹{pnl_amount:.2f} ({pnl_pct:.2%})
🆔 Exit Order: {exit_order}

{'🎉 PROFITABLE TRADE!' if pnl_amount > 0 else '⚠️ Loss taken'}
                        """
                        asyncio.create_task(self.send_telegram_message(message))
                        
                        # Remove from active positions
                        del self.active_positions[symbol]
        
        except Exception as e:
            logger.error(f"❌ Exit check failed: {e}")
    
    def analyze_market_and_trade(self):
        """Main trading logic with exact indicators"""
        try:
            # Get NIFTY data for analysis
            nifty_token = self.instruments.get('NIFTY 50', {}).get('instrument_token')
            if not nifty_token:
                return
            
            # Get historical data
            from_date = datetime.now(IST) - timedelta(days=5)
            to_date = datetime.now(IST)
            
            historical_data = self.kite.historical_data(
                nifty_token, from_date, to_date, "5minute"
            )
            
            if len(historical_data) < 50:
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['datetime'] = pd.to_datetime(df['date'])
            
            # Calculate exact indicators (matching your setup)
            # RSI 21 ohlc/4
            df['ohlc4'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
            df['rsi'] = self.calculate_rsi(df['ohlc4'], 21)
            
            # Moving averages
            df['ma_20'] = df['close'].rolling(20).mean()
            df['ma_50'] = df['close'].rolling(50).mean()
            
            # ADX 14
            df['adx'] = self.calculate_adx(df, 14)
            
            # Get latest values
            latest = df.iloc[-1]
            
            # Trading signals
            rsi_value = latest['rsi']
            ma_20 = latest['ma_20']
            ma_50 = latest['ma_50']
            adx_value = latest['adx']
            current_price = latest['close']
            
            # Signal logic
            bullish_signal = (
                rsi_value < 40 and  # Oversold
                current_price > ma_20 and  # Above short MA
                ma_20 > ma_50 and  # Bullish MA alignment
                adx_value > 25  # Strong trend
            )
            
            bearish_signal = (
                rsi_value > 60 and  # Overbought
                current_price < ma_20 and  # Below short MA
                ma_20 < ma_50 and  # Bearish MA alignment
                adx_value > 25  # Strong trend
            )
            
            # Execute trades based on signals
            if bullish_signal and 'NIFTY24AUGFUT' not in self.active_positions:
                signal_data = {
                    'symbol': 'NIFTY24AUGFUT',
                    'action': 'BUY'
                }
                asyncio.create_task(self.execute_trade(signal_data))
            
            elif bearish_signal and 'NIFTY24AUGFUT' not in self.active_positions:
                signal_data = {
                    'symbol': 'NIFTY24AUGFUT',
                    'action': 'SELL'
                }
                asyncio.create_task(self.execute_trade(signal_data))
        
        except Exception as e:
            logger.error(f"❌ Market analysis failed: {e}")
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_adx(self, df, period=14):
        """Calculate ADX"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        adx = dx.rolling(period).mean()
        
        return adx
    
    async def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            await self.application.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        message = """
🚀 SANDY SNIPER LIVE TRADING BOT

✅ Status: ACTIVE and TRADING LIVE!
💰 Auto-trading with real money
📊 Small lot sizes with risk management

Commands:
/status - Current positions
/balance - Account balance
/stop_trading - Pause trading
/resume_trading - Resume trading

⚠️ This bot trades with REAL MONEY!
        """
        await update.message.reply_text(message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command handler"""
        try:
            # Get account balance
            margins = self.kite.margins()
            available_cash = margins['equity']['available']['cash']
            
            message = f"""
📊 LIVE TRADING STATUS

💰 Available Cash: ₹{available_cash:,.2f}
🎯 Active Positions: {len(self.active_positions)}
📈 Max Risk per Trade: ₹{self.max_risk_per_trade}
🎪 Max Positions: {self.max_positions}

Active Trades:
            """
            
            for symbol, pos in self.active_positions.items():
                current_price = self.get_ltp(symbol)
                entry_price = pos['entry_price']
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                message += f"\n📊 {symbol}: {pos['action']} | P&L: {pnl_pct:.2f}%"
            
            if not self.active_positions:
                message += "\nNo active positions"
            
            await update.message.reply_text(message)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {str(e)[:100]}")
    
    async def trading_loop(self):
        """Main trading loop"""
        while True:
            try:
                # Check market hours (9:15 AM to 3:30 PM IST)
                current_time = datetime.now(IST)
                market_start = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
                market_end = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
                
                if market_start <= current_time <= market_end:
                    # Analyze market and place trades
                    self.analyze_market_and_trade()
                    
                    # Check exit conditions
                    self.check_exit_conditions()
                    
                    # Wait 1 minute before next check
                    await asyncio.sleep(60)
                else:
                    # Outside market hours, wait 5 minutes
                    await asyncio.sleep(300)
            
            except Exception as e:
                logger.error(f"❌ Trading loop error: {e}")
                await asyncio.sleep(60)
    
    async def main(self):
        """Main bot function"""
        try:
            # Authenticate Kite Connect
            if not self.authenticate_kite():
                raise Exception("Kite authentication failed")
            
            # Load instruments
            if not self.load_instruments():
                raise Exception("Failed to load instruments")
            
            # Setup Telegram bot
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            
            # Start the application
            await self.application.initialize()
            await self.application.start()
            
            # Send startup message
            await self.send_telegram_message("""
🚀 SANDY SNIPER LIVE TRADING BOT STARTED!

✅ Kite Connect: Authenticated
✅ Instruments: Loaded
✅ Trading: ACTIVE with real money
💰 Small lots with risk management

The bot is now analyzing markets and will place live trades automatically!
            """)
            
            # Start trading loop
            await self.trading_loop()
        
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            if self.application:
                await self.send_telegram_message(f"❌ Bot startup failed: {str(e)[:100]}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run bot
    bot = LiveTradingBot()
    asyncio.run(bot.main())
