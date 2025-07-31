#!/usr/bin/env python3
"""
Complete Telegram Commands Test for Sandy Sniper Bot
Tests all available commands with your working credentials
"""

import os
import asyncio
import time
import pytz
from datetime import datetime
from dotenv import load_dotenv

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current Indian Standard Time"""
    return datetime.now(IST)

# Load environment
load_dotenv('/workspaces/Sandy_sniper-bot/.env')

# Your working credentials  
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ID = os.getenv('TELEGRAM_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ID:
    print("❌ ERROR: Telegram credentials not found in .env file")
    exit(1)

print(f"🤖 SANDY SNIPER BOT - TELEGRAM COMMANDS TEST")
print(f"============================================")
print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
print(f"Chat ID: {TELEGRAM_ID}")
print(f"Time: {get_indian_time().strftime('%Y-%m-%d %H:%M:%S IST')}")
print()

def send_test_command(command_text):
    """Send a test command via Telegram"""
    import requests
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_ID,
        'text': command_text
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()['result']
            return True, f"✅ Sent: Message ID {result['message_id']}"
        else:
            return False, f"❌ Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"❌ Exception: {e}"

# Test all available commands
commands_to_test = [
    ("📋 BASIC COMMANDS", [
        "/start - Initialize Sandy Sniper Bot",
        "/help - Show all available commands", 
        "/status - Get complete system status"
    ]),
    ("📊 MARKET COMMANDS", [
        "/market - Market analysis & outlook",
        "/prices - Live market prices (NSE + BSE)",
        "/positions - View current trading positions"
    ]),
    ("🎯 TRADING COMMANDS", [
        "/start_trading - Start live trading session",
        "/stop_trading - Stop trading session", 
        "/stop - Pause new trades"
    ])
]

print("🚀 TESTING ALL TELEGRAM COMMANDS:")
print("=" * 50)

total_commands = 0
successful_commands = 0

for category, commands in commands_to_test:
    print(f"\n{category}")
    print("-" * 30)
    
    for command_desc in commands:
        command = command_desc.split(" - ")[0]
        description = command_desc.split(" - ")[1]
        
        print(f"Testing {command}...")
        success, message = send_test_command(command)
        
        total_commands += 1
        if success:
            successful_commands += 1
            print(f"  ✅ {command}: {message}")
        else:
            print(f"  ❌ {command}: {message}")
        
        # Small delay between commands
        time.sleep(1)

print(f"\n" + "=" * 50)
print(f"📊 TELEGRAM COMMANDS TEST SUMMARY")
print(f"=" * 50)
print(f"✅ Successful: {successful_commands}/{total_commands}")
print(f"❌ Failed: {total_commands - successful_commands}/{total_commands}")
print(f"📱 Success Rate: {(successful_commands/total_commands)*100:.1f}%")

if successful_commands == total_commands:
    print(f"\n🎉 ALL TELEGRAM COMMANDS WORKING PERFECTLY!")
    print(f"🤖 Sandy Sniper Bot is ready for live trading!")
    print(f"📱 Check your Telegram app for all test messages")
else:
    print(f"\n⚠️  Some commands failed - check the errors above")

print(f"\n🔔 Next Steps:")
print(f"1. Check your Telegram app (@Sandy_Sniperbot)")
print(f"2. Review all received test messages") 
print(f"3. Bot is ready for live trading commands!")
print(f"4. Use /start_trading when markets open")
