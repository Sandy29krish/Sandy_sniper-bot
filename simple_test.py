#!/usr/bin/env python3
"""
Simple Bot Launcher - Test with Environment Check
"""

print("🚀 Starting Sandy Sniper Bot...")

# Check basic environment
import os
import sys

print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")

# Check environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'NOT_SET')
chat_id = os.getenv('TELEGRAM_ID', 'NOT_SET')

print(f"Bot Token: {'✅ Configured' if bot_token != 'NOT_SET' else '❌ Not set'}")
print(f"Chat ID: {'✅ Configured' if chat_id != 'NOT_SET' else '❌ Not set'}")

# Try to import telegram
try:
    import telegram
    print("✅ Telegram library available")
    
    # Try to create bot instance
    if bot_token != 'NOT_SET':
        bot = telegram.Bot(token=bot_token)
        print("✅ Bot instance created successfully")
    else:
        print("❌ Cannot create bot - token not set")
        
except ImportError:
    print("❌ Telegram library not found")
    print("Please install: pip install python-telegram-bot")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("To configure bot:")
print("1. Set environment variables:")
print("   export TELEGRAM_BOT_TOKEN='your_token'")
print("   export TELEGRAM_ID='your_chat_id'")
print("2. Or create .env file with these values")
print("="*50)
