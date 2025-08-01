#!/usr/bin/env python3
"""
🚀 LIVE TRADING BOT STARTER
Simple, reliable startup script for live trading with real money
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
import pytz

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current Indian time"""
    return datetime.now(IST)

def print_status(message, level="INFO"):
    """Print formatted status message"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{icons.get(level, 'ℹ️')} {message}")

def check_environment():
    """Check environment setup"""
    print_status("CHECKING ENVIRONMENT SETUP", "INFO")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check essential variables
    required_vars = [
        'TELEGRAM_BOT_TOKEN', 'TELEGRAM_ID',
        'KITE_API_KEY', 'KITE_API_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).endswith('_here'):
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Missing credentials: {', '.join(missing_vars)}", "WARNING")
        print_status("Update .env file with real credentials for live trading", "WARNING")
        return False
    
    print_status("Environment setup complete", "SUCCESS")
    return True

def test_telegram_connection():
    """Test Telegram bot connection"""
    print_status("TESTING TELEGRAM CONNECTION", "INFO")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ID')
        
        if not bot_token or not chat_id:
            print_status("Telegram credentials not found", "ERROR")
            return False
        
        # Test bot connection
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print_status(f"Connected to @{bot_info.get('username', 'Unknown')}", "SUCCESS")
            
            # Send startup message
            startup_msg = f"""🚀 **Sandy Sniper Bot LIVE**

⏰ **Startup Time**: {get_indian_time().strftime('%Y-%m-%d %H:%M:%S IST')}
🎯 **Mode**: LIVE TRADING READY
💰 **Warning**: REAL MONEY TRADING ACTIVE

**Available Commands:**
/start - Initialize bot
/status - Trading status
/positions - Current positions
/market - Market data
/stop - Emergency stop

🚨 **Risk Warning**: Live trading with real money!"""
            
            msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            msg_data = {
                'chat_id': chat_id,
                'text': startup_msg,
                'parse_mode': 'Markdown'
            }
            
            msg_response = requests.post(msg_url, json=msg_data, timeout=10)
            if msg_response.status_code == 200:
                print_status("Startup message sent to Telegram", "SUCCESS")
            
            return True
        else:
            print_status(f"Telegram connection failed: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Telegram test failed: {e}", "ERROR")
        return False

def start_trading_bot():
    """Start the main trading bot"""
    print_status("STARTING LIVE TRADING BOT", "INFO")
    
    try:
        # Check if we have the enhanced bot file
        if os.path.exists('enhanced_sniper_swing.py'):
            print_status("Starting enhanced sniper swing bot", "INFO")
            exec(open('enhanced_sniper_swing.py').read())
        elif os.path.exists('sniper_swing.py'):
            print_status("Starting sniper swing bot", "INFO")
            exec(open('sniper_swing.py').read())
        elif os.path.exists('theta_protected_bot.py'):
            print_status("Starting theta protected bot", "INFO")
            exec(open('theta_protected_bot.py').read())
        else:
            print_status("No trading bot file found", "ERROR")
            return False
            
        return True
        
    except Exception as e:
        print_status(f"Bot startup failed: {e}", "ERROR")
        logger.exception("Bot startup error")
        return False

def main():
    """Main startup function"""
    print("\n" + "="*60)
    print("🚀 SANDY SNIPER BOT - LIVE TRADING STARTUP")
    print("="*60)
    print(f"⏰ Startup Time: {get_indian_time().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("🎯 Mode: LIVE TRADING WITH REAL MONEY")
    print("="*60)
    
    # Step 1: Check environment
    if not check_environment():
        print_status("Environment check failed - update credentials", "ERROR")
        print_status("Edit .env file with your real Zerodha and Telegram credentials", "WARNING")
        return False
    
    # Step 2: Test Telegram
    if not test_telegram_connection():
        print_status("Telegram connection failed", "ERROR")
        return False
    
    # Step 3: Start trading bot
    print_status("🚨 STARTING LIVE TRADING BOT 🚨", "WARNING")
    print_status("This will trade with REAL MONEY", "WARNING")
    print_status("Press Ctrl+C to stop", "INFO")
    
    try:
        # Import and start the telegram command server
        from telegram_commands import start_telegram_command_server
        start_telegram_command_server()
        
        print_status("Telegram command server started", "SUCCESS")
        print_status("Bot is now LIVE and monitoring markets", "SUCCESS")
        print_status("Send /start to your Telegram bot to begin", "INFO")
        
        # Keep the script running
        import time
        while True:
            time.sleep(60)  # Check every minute
            current_time = get_indian_time()
            if current_time.hour == 9 and current_time.minute == 0:
                print_status("Market opening - Bot active", "INFO")
            elif current_time.hour == 15 and current_time.minute == 30:
                print_status("Market closing - Bot monitoring", "INFO")
                
    except KeyboardInterrupt:
        print_status("Bot stopped by user", "WARNING")
        return True
    except Exception as e:
        print_status(f"Bot error: {e}", "ERROR")
        logger.exception("Bot runtime error")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print_status("Bot shutdown complete", "INFO")
    else:
        print_status("Bot failed to start properly", "ERROR")
        sys.exit(1)
