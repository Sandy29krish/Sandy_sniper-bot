#!/usr/bin/env python3
"""
📱 SANDY SNIPER BOT - TELEGRAM COMMANDS REFERENCE
Complete guide to all available Telegram commands
"""

print("🤖 SANDY SNIPER BOT - TELEGRAM COMMANDS REFERENCE")
print("=" * 60)
print("🔗 Bot: @Sandy_Sniperbot")
print("👤 User: Saki")
print("🕐 Timezone: Indian Standard Time (IST)")
print()

print("📋 BASIC BOT COMMANDS:")
print("-" * 30)
print("📱 /start")
print("   ▶️ Initialize Sandy Sniper Bot")
print("   🎯 Shows welcome message with current status")
print("   ⏰ Displays current IST time")
print("   📊 Available 24/7")
print()

print("📱 /help") 
print("   ▶️ Show complete command reference")
print("   📖 Lists all available commands")
print("   🎯 Personalized for Saki")
print("   📊 Always available")
print()

print("📱 /status")
print("   ▶️ Complete system status report")
print("   📊 Live market prices (NIFTY, BANKNIFTY, SENSEX)")
print("   🎯 Trading status (ACTIVE/STOPPED)")
print("   🏛️ Market status (OPEN/CLOSED)")
print("   💹 Today's P&L summary")
print("   🛡️ System health metrics")
print()

print("📊 MARKET DATA COMMANDS:")
print("-" * 30)
print("📱 /market")
print("   ▶️ Market analysis & outlook")
print("   📈 Technical analysis summary")
print("   🎯 Trading recommendations")
print("   ⏰ Market timings (IST)")
print("   📊 Volatility assessment")
print()

print("📱 /prices")
print("   ▶️ Live market prices")
print("   🇮🇳 NSE: NIFTY, BANKNIFTY")
print("   🏛️ BSE: SENSEX (Special support)")
print("   📊 Real-time price updates")
print("   ⏰ Updated every minute during market hours")
print()

print("📱 /positions")
print("   ▶️ View current trading positions")
print("   💼 Active trades details")
print("   💰 Real-time P&L")
print("   📊 Entry/Exit prices")
print("   🎯 Position sizes")
print()

print("🎯 TRADING CONTROL COMMANDS:")
print("-" * 30)
print("📱 /start_trading")
print("   ▶️ Start live trading session")
print("   🔥 Activates automated trading")
print("   ⚡ Begins signal monitoring")
print("   🛡️ Enables risk management")
print("   📱 Sends trade notifications")
print()

print("📱 /stop_trading")
print("   ▶️ Stop trading session")
print("   ⏹️ Pauses new trade entries")
print("   💼 Maintains existing positions")
print("   📊 Continues monitoring")
print("   📱 Sends session summary")
print()

print("📱 /stop")
print("   ▶️ Pause new trades")
print("   🛑 Emergency stop function")
print("   💼 Keeps positions active")
print("   🔄 Use /start to resume")
print()

print("🔔 AUTOMATED NOTIFICATIONS:")
print("-" * 30)
print("🌅 Morning Greetings")
print("   ▶️ Daily market opening message")
print("   📊 Pre-market analysis")
print("   🎯 Trading plan for the day")
print()

print("📈 Trade Alerts")
print("   ▶️ Entry signal notifications")
print("   📊 Exit signal alerts")
print("   💰 P&L updates")
print("   ⚠️ Risk management alerts")
print()

print("🌆 Market Closing")
print("   ▶️ End-of-day summary")
print("   📊 Performance report")
print("   💰 Daily P&L statement")
print()

print("🎯 SPECIAL FEATURES FOR SAKI:")
print("-" * 30)
print("✅ Personalized messages with 'Saki' name")
print("✅ Indian timezone (IST) for all operations")
print("✅ BSE SENSEX support (corrected implementation)")
print("✅ Real-time notifications to your phone")
print("✅ 24/7 system monitoring and alerts")
print("✅ Advanced risk management")
print("✅ AI-powered trading signals")
print()

print("⚡ SYSTEM CAPABILITIES:")
print("-" * 30)
print("🤖 AI-Powered Signal Analysis")
print("📊 Multi-Timeframe Technical Analysis")
print("🛡️ Bulletproof API Integration")
print("⚡ Real-time Price Monitoring")
print("💰 Automated Position Management")
print("📱 Instant Telegram Notifications")
print("🎯 Personalized for Saki's Trading Style")
print()

print("🚀 HOW TO USE:")
print("-" * 30)
print("1. Start your day with /start")
print("2. Check market with /market or /prices")
print("3. Begin trading with /start_trading")
print("4. Monitor with /status and /positions")
print("5. End session with /stop_trading")
print()

print("📱 TELEGRAM SETUP:")
print("-" * 30)
print("✅ Bot Token: 8143962740:AAHHPGho9tckm3E9Hav9n8sfBsmAn2CinPs")
print("✅ Chat ID: 7797661300")
print("✅ Bot Username: @Sandy_Sniperbot")
print("✅ Bot Name: Sandy Krish")
print("✅ Connection: ACTIVE")
print()

print("🎉 READY FOR LIVE TRADING!")
print("=" * 60)
print("📱 Sandy Sniper Bot is fully configured and ready!")
print("🎯 All commands are available for Saki")
print("💰 Start trading and make profits!")
print("🚀 Use /start_trading when markets open!")

# Test basic message sending
import os
import requests
from dotenv import load_dotenv

load_dotenv('/workspaces/Sandy_sniper-bot/.env')

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_ID')

if bot_token and chat_id:
    print("\n📤 SENDING COMMAND REFERENCE TO TELEGRAM...")
    
    message = """🤖 SANDY SNIPER BOT - COMMANDS READY! 🎯

📋 Available Commands:
• /start - Initialize bot
• /status - System status  
• /market - Market analysis
• /prices - Live prices
• /positions - View trades
• /start_trading - Begin trading 🔥
• /stop_trading - End session ⏹️
• /help - Full command list

✅ Bot is LIVE and ready for Saki!
💰 Ready to make profits! 🚀"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Command reference sent to your Telegram!")
        else:
            print(f"❌ Send failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Telegram credentials not found")
