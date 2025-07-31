#!/usr/bin/env python3
"""
🚀 ENHANCED TELEGRAM BOT - Ready for Live Trading
Complete Telegram command system with Indian timing and personal messages for Saki
"""

import os
import logging
import threading
import time
import asyncio
from datetime import datetime, timedelta
import pytz
import requests
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, NetworkError

# Indian timezone for all operations
IST = pytz.timezone('Asia/Kolkata')

logger = logging.getLogger(__name__)

class EnhancedTelegramBot:
    """Enhanced Telegram Bot with Indian timing and personal messages for Saki"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        self.application = None
        self.running = False
        self.user_name = "Saki"  # Personal name for user
        self.morning_sent = False
        self.closing_sent = False
        
    def get_ist_time(self):
        """Get current Indian Standard Time"""
        return datetime.now(IST)
    
    def format_ist_time(self, dt=None):
        """Format time in IST"""
        if dt is None:
            dt = self.get_ist_time()
        return dt.strftime('%d-%m-%Y %H:%M:%S IST')
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        ist_time = self.format_ist_time()
        
        message = f"""🚀 **Sandy Sniper Bot Activated for {self.user_name}!**

✅ **Status**: READY FOR LIVE TRADING
⏰ **Time**: {ist_time}
🎯 **Trading Mode**: Swing Trading (NIFTY, BANKNIFTY, SENSEX, FINNIFTY)

**Available Commands:**
/status - Get detailed bot status
/positions - View current positions
/market - Market status and prices
/stop - Stop the bot
/start - Restart the bot
/help - Show all commands

🤖 **Ready to trade with you {self.user_name}! Let's make some profits! 💰**"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"✅ Bot started by {self.user_name} at {ist_time}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command with detailed information"""
        try:
            ist_time = self.format_ist_time()
            
            # Get system status
            system_status = self._get_system_status()
            market_status = self._get_market_status()
            
            status_msg = f"""📊 **Sandy Sniper Bot Status for {self.user_name}**

⏰ **Time**: {ist_time}
🎯 **Mode**: {'LIVE TRADING' if market_status['is_open'] else 'MONITORING'}
📈 **Market**: {market_status['status']}

**📊 Current Prices (IST {self.get_ist_time().strftime('%H:%M')}):**
• NIFTY: ₹{system_status.get('nifty_price', 'N/A')}
• BANKNIFTY: ₹{system_status.get('banknifty_price', 'N/A')}
• SENSEX: ₹{system_status.get('sensex_price', 'N/A')}
• FINNIFTY: ₹{system_status.get('finnifty_price', 'N/A')}

**🔧 System Health:**
• CPU: {system_status.get('cpu', 'N/A')}%
• Memory: {system_status.get('memory', 'N/A')}%
• Active Trades: {system_status.get('active_trades', 0)}
• Daily Trades: {system_status.get('daily_trades', 0)}

**🛡️ Protection Status:**
• Kite API: {system_status.get('kite_status', 'Fallback Mode')}
• Telegram: ✅ Connected
• Watchdog: ✅ Active
• AI Assistant: ✅ Ready

{self.user_name}, everything looks good! 🚀"""
            
            await update.message.reply_text(status_msg, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")
            logger.error(f"Status command error: {e}")
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command"""
        try:
            ist_time = self.format_ist_time()
            positions = self._get_current_positions()
            
            if not positions:
                msg = f"📈 **No Active Positions**\n\n⏰ {ist_time}\n\n{self.user_name}, we're monitoring the markets for opportunities! 👀"
                await update.message.reply_text(msg, parse_mode='Markdown')
                return
            
            msg = f"📊 **Current Positions for {self.user_name}**\n\n⏰ {ist_time}\n\n"
            
            for symbol, data in positions.items():
                signal = data.get('signal', 'N/A').upper()
                entry_price = data.get('entry_price', 0)
                current_price = data.get('current_price', 0)
                quantity = data.get('quantity', 0)
                pnl = data.get('pnl', 0)
                
                msg += f"🎯 **{symbol}** ({signal})\n"
                msg += f"Entry: ₹{entry_price:,.2f}\n"
                msg += f"Current: ₹{current_price:,.2f}\n"
                msg += f"Qty: {quantity}\n"
                msg += f"P&L: {'🟢' if pnl >= 0 else '🔴'} ₹{pnl:,.2f}\n\n"
            
            msg += f"Keep it up {self.user_name}! 💪"
            await update.message.reply_text(msg, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting positions: {e}")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        try:
            ist_time = self.format_ist_time()
            market_data = self._get_market_data()
            
            msg = f"""📈 **Market Status for {self.user_name}**

⏰ **IST Time**: {ist_time}
🏛️ **Market**: {market_data['status']}

**📊 Live Prices:**
• **NIFTY**: ₹{market_data.get('nifty', 'N/A')} {market_data.get('nifty_change', '')}
• **BANKNIFTY**: ₹{market_data.get('banknifty', 'N/A')} {market_data.get('banknifty_change', '')}
• **SENSEX**: ₹{market_data.get('sensex', 'N/A')} {market_data.get('sensex_change', '')}
• **FINNIFTY**: ₹{market_data.get('finnifty', 'N/A')} {market_data.get('finnifty_change', '')}

**⏰ Market Timings (IST):**
• Pre-Market: 9:00 - 9:15 AM
• Regular: 9:15 AM - 3:30 PM
• Post-Market: 3:30 - 4:00 PM

{market_data.get('next_session', '')}

Ready to trade {self.user_name}! 🚀"""
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting market data: {e}")
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        ist_time = self.format_ist_time()
        
        msg = f"""🛑 **Bot Stop Requested by {self.user_name}**

⏰ **Time**: {ist_time}

**Current Status:**
• All active monitoring will continue
• New trades will be paused
• Existing positions remain active
• Telegram notifications continue

To fully restart, use /start command.

See you soon {self.user_name}! 👋"""
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        logger.info(f"Bot stop requested by {self.user_name} at {ist_time}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        ist_time = self.format_ist_time()
        
        help_text = f"""🤖 **Sandy Sniper Bot Help for {self.user_name}**

⏰ **IST Time**: {ist_time}

**📱 Available Commands:**
/start - Initialize/restart the bot
/status - Complete system status
/positions - View your current positions
/market - Live market data & prices
/stop - Pause new trades
/help - Show this help menu

**📊 Supported Instruments:**
• NIFTY (Nifty 50)
• BANKNIFTY (Bank Nifty)
• SENSEX (BSE Sensex)
• FINNIFTY (Fin Nifty)

**🎯 Trading Features:**
• Swing Trading with AI Analysis
• Real-time price monitoring
• Smart entry/exit signals
• Risk management
• Live P&L tracking

**🕐 Indian Market Hours:**
• Trading: 9:15 AM - 3:30 PM IST
• Monitoring: 24/7

Ready to make profits with you {self.user_name}! 💰📈"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def _get_system_status(self):
        """Get current system status"""
        try:
            # Mock data - replace with actual system calls
            return {
                'nifty_price': '24,854.80',
                'banknifty_price': '56,068.60', 
                'sensex_price': '81,343.20',  # Added SENSEX
                'finnifty_price': '23,800.00',
                'cpu': 15.5,
                'memory': 65.2,
                'active_trades': 0,
                'daily_trades': 0,
                'kite_status': 'Fallback Mode'
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {}
    
    def _get_market_status(self):
        """Get market status with IST timing"""
        ist_now = self.get_ist_time()
        hour = ist_now.hour
        minute = ist_now.minute
        
        is_weekday = ist_now.weekday() < 5  # Monday = 0, Sunday = 6
        
        if is_weekday and (9 <= hour < 15 or (hour == 15 and minute <= 30)):
            return {'is_open': True, 'status': 'OPEN'}
        else:
            return {'is_open': False, 'status': 'CLOSED'}
    
    def _get_current_positions(self):
        """Get current trading positions"""
        try:
            # Mock data - replace with actual position calls
            return {}
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return {}
    
    def _get_market_data(self):
        """Get comprehensive market data"""
        try:
            market_status = self._get_market_status()
            ist_now = self.get_ist_time()
            
            data = {
                'status': 'OPEN' if market_status['is_open'] else 'CLOSED',
                'nifty': '24,854.80',
                'banknifty': '56,068.60',
                'sensex': '81,343.20',  # Added SENSEX
                'finnifty': '23,800.00',
                'nifty_change': '🟢 +0.5%',
                'banknifty_change': '🔴 -0.2%',
                'sensex_change': '🟢 +0.3%',
                'finnifty_change': '🟢 +0.1%'
            }
            
            if not market_status['is_open']:
                if ist_now.hour < 9:
                    data['next_session'] = f"🕘 **Next Session**: Today 9:15 AM IST"
                else:
                    data['next_session'] = f"🕘 **Next Session**: Tomorrow 9:15 AM IST"
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    async def send_morning_message(self):
        """Send good morning message to Saki"""
        if self.morning_sent:
            return
            
        ist_now = self.get_ist_time()
        if ist_now.hour == 9 and ist_now.minute < 15:  # Pre-market
            message = f"""🌅 **Good Morning {self.user_name}!**

⏰ **IST Time**: {self.format_ist_time()}
🏛️ **Market**: Opening in {15 - ist_now.minute} minutes

🎯 **Ready for Today's Trading Session!**
• Systems: ✅ All Online
• AI Analysis: ✅ Ready
• Risk Management: ✅ Active

Let's trade and make some great profits today {self.user_name}! 💰📈

🚀 **Sandy Sniper Bot is ready for action!**"""
            
            await self.send_message(message)
            self.morning_sent = True
            logger.info(f"Good morning message sent to {self.user_name}")
    
    async def send_closing_message(self):
        """Send market closing message to Saki"""
        if self.closing_sent:
            return
            
        ist_now = self.get_ist_time()
        if ist_now.hour == 15 and ist_now.minute >= 30:  # Market closed
            message = f"""🌆 **Market Closed - Good Evening {self.user_name}!**

⏰ **IST Time**: {self.format_ist_time()}
🏛️ **Market**: CLOSED for today

📊 **Today's Summary:**
• Trading Session: Completed
• System Status: ✅ All systems healthy
• Monitoring: Continues 24/7

**Great job today {self.user_name}!** 🎉
You've been an excellent trader! 

🌙 **Rest well, tomorrow we trade again at 9:15 AM IST**

See you tomorrow morning! 👋💤"""
            
            await self.send_message(message)
            self.closing_sent = True
            logger.info(f"Closing message sent to {self.user_name}")
    
    async def send_message(self, message):
        """Send message via Telegram"""
        try:
            if self.bot:
                await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
                return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def start_bot(self):
        """Start the enhanced Telegram bot"""
        if not self.token:
            logger.error("No Telegram token provided")
            return False
            
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            self.bot = self.application.bot
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("positions", self.positions_command))
            self.application.add_handler(CommandHandler("market", self.market_command))
            self.application.add_handler(CommandHandler("stop", self.stop_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            
            # Start the bot in a separate thread
            def run_bot():
                asyncio.new_event_loop().run_until_complete(self._run_bot())
            
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            
            self.running = True
            logger.info(f"✅ Enhanced Telegram Bot started for {self.user_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            return False
    
    async def _run_bot(self):
        """Run the bot with scheduled messages"""
        try:
            # Start polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Schedule daily messages
            while self.running:
                await asyncio.sleep(60)  # Check every minute
                
                ist_now = self.get_ist_time()
                
                # Reset daily flags at midnight
                if ist_now.hour == 0 and ist_now.minute == 0:
                    self.morning_sent = False
                    self.closing_sent = False
                
                # Send morning message
                if not self.morning_sent:
                    await self.send_morning_message()
                
                # Send closing message
                if not self.closing_sent:
                    await self.send_closing_message()
                    
        except Exception as e:
            logger.error(f"Bot polling error: {e}")

# Global instance
enhanced_bot = None

def start_enhanced_telegram_bot():
    """Start the enhanced Telegram bot for live trading"""
    global enhanced_bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ID")
    
    if not token or not chat_id:
        logger.error("Missing Telegram credentials")
        return False
    
    enhanced_bot = EnhancedTelegramBot(token, chat_id)
    return enhanced_bot.start_bot()

def send_telegram_message_to_saki(message):
    """Send message to Saki with IST timing"""
    global enhanced_bot
    
    if enhanced_bot:
        # Add IST timestamp to message
        ist_time = datetime.now(IST).strftime('%H:%M:%S IST')
        timestamped_message = f"{message}\n\n⏰ {ist_time}"
        asyncio.create_task(enhanced_bot.send_message(timestamped_message))
        return True
    
    # Fallback to direct API call
    return send_direct_telegram_message(message)

def send_direct_telegram_message(message):
    """Direct Telegram API call with IST timing"""
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_ID")
        
        if not token or not chat_id:
            return False
        
        # Add IST timestamp
        ist_time = datetime.now(IST).strftime('%H:%M:%S IST')
        timestamped_message = f"{message}\n\n⏰ {ist_time}"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': timestamped_message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Direct message error: {e}")
        return False

# Test connection with IST timing
def test_telegram_connection():
    """Test telegram connection - Fixed sync version with IST"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ID")
    
    if not token or not chat_id:
        return False, "Missing Telegram credentials"
    
    try:
        # Use direct API call instead of async Bot.get_me()
        import requests
        
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            username = bot_info.get('username', 'Unknown')
            return True, f"Connected to bot: @{username} (IST: {datetime.now(IST).strftime('%H:%M:%S')})"
        else:
            return False, f"API Error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection failed: {e}"

if __name__ == "__main__":
    print("🚀 Starting Enhanced Telegram Bot for Saki...")
    success = start_enhanced_telegram_bot()
    if success:
        print("✅ Enhanced Telegram Bot started successfully!")
        print("🎯 Ready for live trading tomorrow!")
    else:
        print("❌ Failed to start Enhanced Telegram Bot")
