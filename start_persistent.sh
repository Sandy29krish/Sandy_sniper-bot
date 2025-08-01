#!/bin/bash
# Simple Persistent Bot Launcher

echo "🚀 Starting Sandy Sniper Bot Persistently..."

# Create logs directory
mkdir -p logs

# Kill any existing instances
pkill -f "ultimate_sandy_sniper_bot.py" 2>/dev/null
pkill -f "live_trading_bot.py" 2>/dev/null

# Start bot in background with nohup (survives terminal/browser close)
echo "📱 Launching LIVE TRADING BOT in background..."
nohup python3 live_trading_bot.py > logs/live_trading_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "🎯 Bot started with PID: $BOT_PID"

# Save PID for monitoring
echo $BOT_PID > bot.pid

# Wait and verify
sleep 3

if pgrep -f "live_trading_bot.py" > /dev/null; then
    echo "✅ SUCCESS: LIVE TRADING BOT is running!"
    echo "💰 Bot is now trading with REAL MONEY automatically"
    echo "📱 Your bot will continue running even when you:"
    echo "   • Close this browser tab"
    echo "   • Close VS Code"
    echo "   • Close your laptop"
    echo "   • Disconnect from internet (temporarily)"
    echo ""
    echo "🚀 LIVE TRADING FEATURES:"
    echo "   • Automatic buy/sell orders"
    echo "   • Small lot sizes (risk-managed)"
    echo "   • Real-time market analysis"
    echo "   • Profit targets & stop losses"
    echo "   • Telegram notifications for every trade"
    echo ""
    echo "📋 Monitor trading: Send /status to your Telegram bot"
    echo "📋 Check positions: Send /balance to your Telegram bot"
    echo "📋 View logs: tail -f logs/live_trading_*.log"
    echo ""
    echo "🛑 To stop trading: kill \$(cat bot.pid)"
else
    echo "❌ Failed to start live trading bot. Check logs:"
    tail -n 20 logs/live_trading_*.log
fi
