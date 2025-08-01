#!/usr/bin/env python3
"""
🚀 DIRECT BOT LAUNCHER - Sandy Sniper Bot
Minimal launcher for immediate startup
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 SANDY SNIPER BOT - DIRECT START")
    print("=" * 40)
    
    # Load environment from .env
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    # Check credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_ID', '')
    
    if not bot_token or bot_token == 'your_bot_token_here':
        print("❌ Bot token not configured")
        return False
        
    if not chat_id or chat_id == 'your_chat_id_here':
        print("❌ Chat ID not configured")
        return False
    
    print(f"✅ Bot Token: Configured")
    print(f"✅ Chat ID: {chat_id}")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", 
                       "python-telegram-bot", "pandas", "pytz", "requests", "python-dotenv"], 
                      check=True)
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"⚠️ Dependency installation: {e}")
    
    # Kill existing processes
    try:
        subprocess.run(["pkill", "-f", "theta_protected_bot.py"], 
                      stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "ultimate_sandy_sniper_bot.py"], 
                      stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except:
        pass
    
    # Start bot
    print("🎯 Starting bot...")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Start in background
    log_file = f"logs/bot_{int(time.time())}.log"
    
    try:
        process = subprocess.Popen([
            sys.executable, "theta_protected_bot.py"
        ], stdout=open(log_file, 'w'), stderr=subprocess.STDOUT)
        
        # Save PID
        with open("bot.pid", "w") as f:
            f.write(str(process.pid))
        
        print(f"✅ Bot started with PID: {process.pid}")
        print(f"📊 Log file: {log_file}")
        print("📱 Send /start to your Telegram bot to test")
        
        # Wait a moment to check if it started successfully
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Bot is running successfully!")
            print("🚀 YOUR BOT IS ALIVE AND READY FOR TRADING SIGNALS!")
            return True
        else:
            print("❌ Bot stopped unexpectedly")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "=" * 40)
        print("🎯 SANDY SNIPER BOT STATUS: ACTIVE")
        print("Your bot will continue running in the background")
        print("It will provide trading signals and analysis")
        print("=" * 40)
    else:
        print("\n❌ Bot startup failed. Check configuration.")
