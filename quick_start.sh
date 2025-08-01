#!/bin/bash
# 🚀 SANDY SNIPER BOT - QUICK START

echo "🚀 SANDY SNIPER BOT - STARTING..."
echo "=================================="

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment loaded from .env"
fi

# Check if bot token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_bot_token_here" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not configured"
    exit 1
fi

# Check if chat ID is set
if [ -z "$TELEGRAM_ID" ] || [ "$TELEGRAM_ID" = "your_chat_id_here" ]; then
    echo "❌ TELEGRAM_ID not configured"
    exit 1
fi

echo "✅ Bot Token: Configured"
echo "✅ Chat ID: $TELEGRAM_ID"

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -q python-telegram-bot pandas pytz requests python-dotenv

# Kill any existing bot process
pkill -f "theta_protected_bot.py" 2>/dev/null || true
pkill -f "ultimate_sandy_sniper_bot.py" 2>/dev/null || true

echo "🎯 Starting bot in background..."

# Start the bot with nohup
nohup python3 theta_protected_bot.py > logs/bot_$(date +%Y%m%d_%H%M%S).log 2>&1 &
BOT_PID=$!

echo "✅ Bot started with PID: $BOT_PID"
echo "📱 Send /start to your Telegram bot to test"
echo "📊 Check logs: tail -f logs/bot_*.log"

# Save PID for later reference
echo $BOT_PID > bot.pid

echo "=================================="
echo "🚀 SANDY SNIPER BOT IS ALIVE!"
echo "Your bot will continue running even if you close this terminal"
