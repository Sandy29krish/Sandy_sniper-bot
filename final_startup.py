#!/usr/bin/env python3
"""
🎯 SANDY SNIPER BOT - COMPLETE STATUS & STARTUP
Final comprehensive system to get your bot alive and trading
"""

import os
import sys
import json
import time
from datetime import datetime

# Force output flushing
import sys
sys.stdout.flush()

def print_status(message):
    print(message)
    sys.stdout.flush()

def main():
    print_status("🚀 SANDY SNIPER BOT - COMPREHENSIVE STARTUP")
    print_status("=" * 50)
    
    # 1. Environment Check
    print_status("🔧 ENVIRONMENT CHECK:")
    
    # Load .env file
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    os.environ[key] = value
    
    bot_token = env_vars.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = env_vars.get('TELEGRAM_ID', '')
    
    print_status(f"Bot Token: {'✅ SET' if bot_token and bot_token != 'your_bot_token_here' else '❌ MISSING'}")
    print_status(f"Chat ID: {'✅ SET (' + chat_id + ')' if chat_id and chat_id != 'your_chat_id_here' else '❌ MISSING'}")
    
    if not bot_token or not chat_id:
        print_status("❌ CONFIGURATION ERROR: Missing credentials")
        return False
    
    # 2. Dependencies
    print_status("\n📦 DEPENDENCIES:")
    
    try:
        import telegram
        print_status("✅ python-telegram-bot: Available")
    except ImportError:
        print_status("⚠️ Installing python-telegram-bot...")
        os.system("pip install python-telegram-bot")
    
    try:
        import pandas
        print_status("✅ pandas: Available")
    except ImportError:
        print_status("⚠️ Installing pandas...")
        os.system("pip install pandas")
    
    try:
        import pytz
        print_status("✅ pytz: Available")
    except ImportError:
        print_status("⚠️ Installing pytz...")
        os.system("pip install pytz")
    
    # 3. Bot Test
    print_status("\n🤖 BOT CONNECTION TEST:")
    
    try:
        import telegram
        bot = telegram.Bot(token=bot_token)
        bot_info = bot.get_me()
        print_status(f"✅ Bot Connected: @{bot_info.username}")
        print_status(f"✅ Bot Name: {bot_info.first_name}")
    except Exception as e:
        print_status(f"❌ Bot Connection Failed: {str(e)[:50]}...")
        return False
    
    # 4. Kill existing processes
    print_status("\n🔄 PROCESS CLEANUP:")
    os.system("pkill -f 'theta_protected_bot.py' 2>/dev/null || true")
    os.system("pkill -f 'ultimate_sandy_sniper_bot.py' 2>/dev/null || true")
    print_status("✅ Cleaned up existing bot processes")
    
    # 5. Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # 6. Start bot
    print_status("\n🚀 STARTING BOT:")
    
    import subprocess
    log_file = f"logs/bot_{int(time.time())}.log"
    
    # Start the bot
    cmd = [sys.executable, "theta_protected_bot.py"]
    
    try:
        with open(log_file, 'w') as log_f:
            process = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd()
            )
        
        # Save PID
        with open("bot.pid", "w") as f:
            f.write(str(process.pid))
        
        print_status(f"✅ Bot Process Started: PID {process.pid}")
        print_status(f"📊 Log File: {log_file}")
        
        # Wait and check
        time.sleep(3)
        
        if process.poll() is None:
            print_status("✅ Bot is running successfully!")
            
            # Create status file
            status = {
                "status": "RUNNING",
                "pid": process.pid,
                "started": datetime.now().isoformat(),
                "log_file": log_file,
                "bot_username": bot_info.username,
                "chat_id": chat_id
            }
            
            with open("bot_status.json", "w") as f:
                json.dump(status, f, indent=2)
            
            print_status("\n" + "=" * 50)
            print_status("🎯 SANDY SNIPER BOT STATUS: ACTIVE")
            print_status("🚀 YOUR BOT IS ALIVE AND READY!")
            print_status("📱 Send /start to your Telegram bot to test")
            print_status("📊 Bot provides trading signals and analysis")
            print_status("⚡ Bot runs persistently in background")
            print_status("=" * 50)
            
            return True
        else:
            print_status("❌ Bot stopped unexpectedly")
            # Try to show error from log
            try:
                with open(log_file, 'r') as f:
                    error_content = f.read()
                    if error_content:
                        print_status(f"Error details: {error_content[:200]}...")
            except:
                pass
            return False
            
    except Exception as e:
        print_status(f"❌ Failed to start bot: {e}")
        return False

if __name__ == "__main__":
    main()
