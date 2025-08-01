#!/usr/bin/env python3
"""
🎯 SANDY SNIPER BOT - STATUS CHECKER
Check if your bot is alive and provide control options
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def check_process(pid):
    """Check if a process is running"""
    try:
        # Send signal 0 to check if process exists
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False

def get_bot_status():
    """Get comprehensive bot status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "bot_alive": False,
        "pid": None,
        "log_files": [],
        "configuration": {}
    }
    
    # Check PID file
    if os.path.exists("bot.pid"):
        try:
            with open("bot.pid", "r") as f:
                pid = f.read().strip()
                status["pid"] = pid
                status["bot_alive"] = check_process(pid)
        except:
            pass
    
    # Check configuration
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "TELEGRAM_BOT_TOKEN" in line and "=" in line:
                    _, token = line.strip().split("=", 1)
                    status["configuration"]["bot_token"] = "✅ SET" if token and token != "your_bot_token_here" else "❌ MISSING"
                elif "TELEGRAM_ID" in line and "=" in line:
                    _, chat_id = line.strip().split("=", 1)
                    status["configuration"]["chat_id"] = chat_id if chat_id and chat_id != "your_chat_id_here" else "❌ MISSING"
    
    # Check log files
    if os.path.exists("logs"):
        log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
        status["log_files"] = sorted(log_files, reverse=True)[:5]  # Latest 5 logs
    
    return status

def main():
    print("🎯 SANDY SNIPER BOT - STATUS CHECK")
    print("=" * 50)
    
    status = get_bot_status()
    
    print(f"⏰ Check Time: {status['timestamp']}")
    print(f"🤖 Bot Status: {'🟢 ALIVE' if status['bot_alive'] else '🔴 NOT RUNNING'}")
    
    if status['pid']:
        print(f"🆔 Process ID: {status['pid']}")
    
    # Configuration status
    print("\n🔧 Configuration:")
    for key, value in status['configuration'].items():
        print(f"   {key}: {value}")
    
    # Log files
    if status['log_files']:
        print(f"\n📊 Recent Logs ({len(status['log_files'])}):")
        for log in status['log_files'][:3]:
            print(f"   📄 {log}")
    
    # Actions
    print("\n🎮 Available Actions:")
    
    if status['bot_alive']:
        print("✅ YOUR BOT IS ALIVE AND RUNNING!")
        print("📱 Send /start to your Telegram bot to interact")
        print("💬 Use /signals to get current market analysis")
        print("📈 Use /status to see trading conditions")
        
        # Show recent log tail
        if status['log_files']:
            latest_log = status['log_files'][0]
            print(f"\n📊 Latest Log ({latest_log}):")
            try:
                with open(f"logs/{latest_log}", "r") as f:
                    lines = f.readlines()
                    for line in lines[-5:]:  # Last 5 lines
                        print(f"   {line.strip()}")
            except:
                print("   (Unable to read log)")
    else:
        print("❌ Bot is not running")
        print("🚀 To start: python3 final_startup.py")
        print("🔧 To configure: Edit .env file with your credentials")
    
    print("\n" + "=" * 50)
    
    # Save status to file
    with open("bot_status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    return status['bot_alive']

if __name__ == "__main__":
    main()
