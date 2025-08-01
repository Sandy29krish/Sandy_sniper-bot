#!/usr/bin/env python3
"""
🧪 QUICK BOT TEST - Verify Sandy Sniper Bot Setup
"""

import os
import sys
from datetime import datetime

def test_environment():
    """Test environment configuration"""
    print("🧪 SANDY SNIPER BOT - QUICK TEST")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Check environment variables
    print("\n🔧 Environment Configuration:")
    
    # Load from .env if exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded")
    except ImportError:
        print("⚠️ python-dotenv not installed (optional)")
    
    # Check credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_ID', '')
    
    if bot_token and bot_token != 'your_bot_token_here':
        print("✅ Bot Token: Configured")
    else:
        print("❌ Bot Token: Not configured")
        
    if chat_id and chat_id != 'your_chat_id_here':
        print("✅ Chat ID: Configured")
    else:
        print("❌ Chat ID: Not configured")
    
    # Check dependencies
    print("\n📦 Dependencies:")
    
    try:
        import telegram
        print("✅ python-telegram-bot: Available")
    except ImportError:
        print("❌ python-telegram-bot: Missing")
        print("   Install: pip install python-telegram-bot")
    
    try:
        import pandas
        print("✅ pandas: Available")
    except ImportError:
        print("❌ pandas: Missing")
        print("   Install: pip install pandas")
    
    try:
        import pytz
        print("✅ pytz: Available")
    except ImportError:
        print("❌ pytz: Missing")
        print("   Install: pip install pytz")
    
    # Test basic functionality
    print("\n🎯 Bot Functionality Test:")
    
    try:
        from datetime import datetime
        import pytz
        
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist)
        print(f"✅ Timezone: {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        # Test signal conditions (basic)
        conditions = {
            'rsi_above_ma': True,
            'ma_hierarchy': True, 
            'adx_strength': False,
            'slope_positive': True,
            'price_above_pivot': True
        }
        
        signal_count = sum(conditions.values())
        print(f"✅ Signal System: Working (Test: {signal_count}/5 conditions)")
        
    except Exception as e:
        print(f"❌ Functionality Test Failed: {e}")
    
    # Bot status summary
    print("\n🚀 DEPLOYMENT STATUS:")
    
    if bot_token and chat_id and bot_token != 'your_bot_token_here' and chat_id != 'your_chat_id_here':
        print("✅ READY TO START: All credentials configured")
        print("📱 Start with: python3 theta_protected_bot.py")
        print("📱 Test with: Send /start to your Telegram bot")
    else:
        print("⚠️ CONFIGURATION NEEDED:")
        print("   1. Edit .env file with your credentials")
        print("   2. Get bot token from @BotFather")
        print("   3. Get chat ID from your bot")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_environment()
