#!/bin/bash

echo "🎯 PERSISTENT BOT DEPLOYMENT STATUS"
echo "=" * 50

echo "📍 Current Directory: $(pwd)"
echo "📅 Date: $(date)"
echo ""

echo "📁 Available Bot Files:"
ls -la *.py | grep -E "(theta_protected_bot|ultimate_sandy_sniper|working_telegram)" | head -5

echo ""
echo "📦 Python Dependencies Check:"
python3 -c "
try:
    import telegram
    print('✅ python-telegram-bot: Available')
except ImportError:
    print('❌ python-telegram-bot: Missing')

try:
    import pandas
    print('✅ pandas: Available')
except ImportError:
    print('❌ pandas: Missing')

try:
    import asyncio
    print('✅ asyncio: Available')
except ImportError:
    print('❌ asyncio: Missing')
" 2>/dev/null || echo "⚠️ Python dependency check failed"

echo ""
echo "🔧 Environment Configuration:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q "TELEGRAM_BOT_TOKEN.*=" .env && ! grep -q "your_bot_token_here" .env; then
        echo "✅ Bot token configured"
    else
        echo "❌ Bot token not configured"
    fi
    if grep -q "TELEGRAM_ID.*=" .env && ! grep -q "your_chat_id_here" .env; then
        echo "✅ Chat ID configured" 
    else
        echo "❌ Chat ID not configured"
    fi
else
    echo "❌ .env file missing"
fi

echo ""
echo "🤖 Running Processes:"
if pgrep -f "bot.py" > /dev/null; then
    echo "✅ Bot processes found:"
    ps aux | grep -E "(bot\.py|telegram)" | grep -v grep | head -3
else
    echo "❌ No bot processes running"
fi

echo ""
echo "📋 Process Status:"
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Bot running with PID: $PID"
    else
        echo "❌ PID file exists but process not running"
        rm bot.pid
    fi
else
    echo "⚠️ No PID file found"
fi

echo ""
echo "📁 Log Files:"
if [ -d logs ]; then
    ls -la logs/ | tail -5
else
    echo "❌ No logs directory"
    mkdir -p logs
    echo "✅ Created logs directory"
fi

echo ""
echo "🚀 SIMPLE DEPLOYMENT COMMANDS:"
echo "1. Start persistently:    nohup python3 theta_protected_bot.py > logs/bot.log 2>&1 &"
echo "2. Check if running:      pgrep -f 'theta_protected_bot.py'"
echo "3. View logs:            tail -f logs/bot.log"
echo "4. Stop bot:             pkill -f 'theta_protected_bot.py'"
echo ""
echo "🎯 Your bot will run even when you close the browser!"
