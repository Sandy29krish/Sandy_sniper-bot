"""
Telegram Commands Handler for Sniper Swing Bot
Provides command server and telegram connectivity functions
"""

import os
import logging
import threading
import time
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import TelegramError, NetworkError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TelegramCommandServer:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        self.application = None
        self.running = False
        
    async def start_command(self, update, context):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 Sniper Swing Bot is running!\n"
            "Available commands:\n"
            "/status - Get bot status\n"
            "/positions - View current positions\n"
            "/stop - Stop the bot\n"
            "/help - Show this help"
        )
    
    async def status_command(self, update, context):
        """Handle /status command"""
        try:
            # Import here to avoid circular imports
            from sniper_swing import StateManager
            state_manager = StateManager()
            positions = state_manager.state.get("positions", {})
            daily_trades = state_manager.state.get("daily_trade_count", 0)
            
            status_msg = f"📊 Bot Status:\n"
            status_msg += f"Active Positions: {len(positions)}\n"
            status_msg += f"Daily Trades: {daily_trades}\n"
            status_msg += f"Market Status: {'Open' if self._is_market_open() else 'Closed'}"
            
            await update.message.reply_text(status_msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")
    
    async def positions_command(self, update, context):
        """Handle /positions command"""
        try:
            from sniper_swing import StateManager
            state_manager = StateManager()
            positions = state_manager.state.get("positions", {})
            
            if not positions:
                await update.message.reply_text("📈 No active positions")
                return
            
            msg = "📊 Current Positions:\n\n"
            for symbol, data in positions.items():
                signal = data.get('signal', 'N/A')
                entry_price = data.get('entry_price', 0)
                quantity = data.get('quantity', 0)
                strike = data.get('strike', 'N/A')
                
                msg += f"🎯 {symbol} ({signal.upper()})\n"
                msg += f"Strike: {strike}\n"
                msg += f"Entry: ₹{entry_price}\n"
                msg += f"Qty: {quantity}\n\n"
            
            await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting positions: {e}")
    
    async def help_command(self, update, context):
        """Handle /help command"""
        help_text = """
🤖 Sniper Swing Bot Commands:

/start - Initialize bot
/status - Current bot status
/positions - View active positions  
/stop - Stop the bot
/help - Show this help

📊 Bot monitors NIFTY, BANKNIFTY, SENSEX, FINNIFTY for swing trading opportunities using advanced technical analysis.
        """
        await update.message.reply_text(help_text)
    
    def _is_market_open(self):
        """Check if market is currently open"""
        try:
            from market_timing import is_market_open
            return is_market_open()
        except:
            return False
    
    async def error_handler(self, update, context):
        """Handle errors in telegram bot"""
        logger.error(f"Telegram bot error: {context.error}")
    
    def start_server(self):
        """Start the telegram command server"""
        if not self.token:
            logger.warning("No Telegram token provided, skipping command server")
            return
            
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("positions", self.positions_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            # Start the bot
            self.running = True
            logger.info("🤖 Telegram command server started")
            self.application.run_polling()
            
        except Exception as e:
            logger.error(f"Failed to start Telegram command server: {e}")
            self.running = False

def start_telegram_command_server():
    """Start telegram command server in background thread"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ID")
    
    if not token:
        logger.warning("No Telegram token found, skipping command server")
        return
    
    server = TelegramCommandServer(token, chat_id)
    
    def run_server():
        try:
            server.start_server()
        except Exception as e:
            logger.error(f"Telegram server error: {e}")
    
    # Run in daemon thread
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    logger.info("🚀 Telegram command server thread started")

def test_telegram_connection():
    """Test telegram connection"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ID")
    
    if not token or not chat_id:
        return False, "Missing Telegram credentials"
    
    try:
        bot = Bot(token=token)
        # Try to get bot info
        bot_info = bot.get_me()
        return True, f"Connected to bot: {bot_info.username}"
    except Exception as e:
        return False, f"Connection failed: {e}"

def send_telegram_message(message):
    """Send a message via telegram"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ID")
    
    if not token or not chat_id:
        logger.warning("Missing Telegram credentials")
        return False
    
    try:
        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False

if __name__ == "__main__":
    # Test the telegram connection
    success, message = test_telegram_connection()
    print(f"Telegram test: {message}")
    
    if success:
        start_telegram_command_server()
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping telegram server...")
