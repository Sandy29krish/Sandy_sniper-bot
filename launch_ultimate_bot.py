#!/usr/bin/env python3
"""
🚀 ULTIMATE SANDY SNIPER BOT LAUNCHER
Quick start script for your one robust trading bot
"""

import subprocess
import sys
import os

def main():
    print("""
🎯 ULTIMATE SANDY SNIPER BOT v6.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ONE ROBUST BOT for all trading needs
📊 Futures Analysis → Options Trading
🔄 Auto Rollover (7 days before expiry)
💰 Live trading with risk management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Starting your core strategy...
""")
    
    # Check environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return
    
    # Optional Kite Connect variables
    kite_vars = ['KITE_API_KEY', 'KITE_API_SECRET', 'KITE_ACCESS_TOKEN']
    missing_kite = [var for var in kite_vars if not os.getenv(var)]
    
    if missing_kite:
        print(f"⚠️  Kite Connect not configured: {', '.join(missing_kite)}")
        print("Bot will run in SIMULATION mode")
    else:
        print("✅ Kite Connect configured - LIVE TRADING mode")
    
    print("\n🚀 Starting Ultimate Sandy Sniper Bot...")
    
    # Launch the bot
    try:
        subprocess.run([sys.executable, 'ultimate_sandy_sniper.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed: {e}")

if __name__ == "__main__":
    main()
