#!/bin/bash
# Simple Persistent Bot Launcher

echo "🚀 Starting Sandy Sniper Bot Persistently..."

# Create logs directory
mkdir -p logs

# Kill any existing instances
pkill -f "ultimate_sandy_sniper_bot.py" 2>/dev/null

# Start bot in background with nohup (survives terminal/browser close)
echo "📱 Launching bot in background..."
nohup python3 ultimate_sandy_sniper_bot.py > logs/persistent_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "🎯 Bot started with PID: $BOT_PID"

# Save PID for monitoring
echo $BOT_PID > bot.pid

# Wait and verify
sleep 3

if pgrep -f "ultimate_sandy_sniper_bot.py" > /dev/null; then
    echo "✅ SUCCESS: Bot is running persistently!"
    echo "📱 Your bot will continue running even when you:"
    echo "   • Close this browser tab"
    echo "   • Close VS Code"
    echo "   • Close your laptop"
    echo "   • Disconnect from internet (temporarily)"
    echo ""
    echo "📋 Test your bot: Send /start to your Telegram bot"
    echo "📋 Check status: cat bot.pid && ps -p \$(cat bot.pid)"
    echo "📋 View logs: tail -f logs/persistent_*.log"
    echo ""
    echo "🛑 To stop: kill \$(cat bot.pid)"
else
    echo "❌ Failed to start bot. Check logs:"
    tail -n 20 logs/persistent_*.log
fi
