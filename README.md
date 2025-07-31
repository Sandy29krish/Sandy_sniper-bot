
# 🎯 Ultimate Sandy Sniper Bot v5.0

**Complete automated trading analysis system with exact chart indicator matching and cross-device chat history.**

## 🚀 Key Features

### 📊 Exact Chart Indicator Replication
- **RSI (21, ohlc/4)** - Exact match to your trading charts
- **MA (14,RSI), MA (26,RSI), MA (9,RSI)** - All moving averages of RSI
- **ADX (14,14,y,n)** - Precise ADX parameters with DI calculations
- **Price Volume MA** - Volume-weighted moving average
- **LR Slope (21,H)** - Linear regression slope using high prices
- **Daily CPR Values** - Central Pivot Range with all levels

### 🤖 Complete Automation
- ✅ **Cross-Device Chat History** - Continue conversations on any device
- ✅ **Auto Rollover Management** - AI-optimized 7-day threshold
- ✅ **Theta Decay Protection** - Smart OTM selection to prevent rapid decay
- ✅ **24/7 Monitoring** - Background analysis and alerts
- ✅ **GitHub Auto-Deployment** - Push-to-deploy workflow

### 📱 Multi-Device Continuity
Start a conversation on your laptop, continue on mobile, switch to desktop - your chat history follows you everywhere. The bot remembers your preferences, analysis requests, and conversation context across all devices.

## 🤖 Bot Commands

```bash
/start      # Initialize with chat history context
/analysis   # Complete 4-instrument analysis with exact indicators
/nifty      # NIFTY specific analysis
/banknifty  # BANKNIFTY specific analysis  
/finnifty   # FINNIFTY specific analysis
/sensex     # SENSEX specific analysis
/rollover   # Auto rollover status for all instruments
/signals    # Quick signal summary
/history    # Your cross-device chat history
/stop       # Emergency stop
```

## 🔧 Quick Start

```bash
# 1. Set environment variables in GitHub Secrets
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ID=your_telegram_chat_id

# 2. Run the ultimate bot
python ultimate_sandy_sniper_bot.py

# 3. Start in Telegram
/start
```

## 🎯 Ready to Trade!

Your Ultimate Sandy Sniper Bot v5.0 is now ready with:

- **Exact chart indicator matching** ✅
- **Cross-device chat history** ✅  
- **Automatic rollover management** ✅
- **Complete automation** ✅
- **GitHub deployment pipeline** ✅

**Start with:** `/start` in Telegram and experience the future of automated trading analysis!
