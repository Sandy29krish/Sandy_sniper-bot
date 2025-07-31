#!/bin/bash
echo "🚀 Auto-starting Sandy Sniper Bot in Codespace..."

# Check if credentials are configured
if [ -f .env ]; then
    source .env
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ "$TELEGRAM_BOT_TOKEN" != "your_bot_token_here" ]; then
        echo "✅ Credentials found, starting bot..."
        
        # Start bot in background using nohup
        nohup python3 ultimate_sandy_sniper_bot.py > logs/codespace_$(date +%Y%m%d_%H%M%S).log 2>&1 &
        
        # Save PID for monitoring
        echo $! > bot.pid
        
        echo "🎯 Bot started with PID: $(cat bot.pid)"
        echo "📱 Your bot is now running persistently!"
        echo "📱 Test with /start in Telegram"
        echo "📋 Check logs: tail -f logs/codespace_*.log"
        
        # Wait a moment and verify it's running
        sleep 3
        if pgrep -f "ultimate_sandy_sniper_bot.py" > /dev/null; then
            echo "✅ Bot is running successfully in background"
            echo "🌐 Bot will continue running even if you close the browser!"
        else
            echo "❌ Bot failed to start - check logs for errors"
        fi
    else
        echo "⚠️ Please configure your credentials in .env file"
        echo "📝 Copy from .env.template and add your bot token"
    fi
else
    echo "⚠️ No .env file found - please create one with your credentials"
fi
