
# 🎯 ULTIMATE SANDY SNIPER BOT v6.0

**ONE ROBUST BOT FOR ALL YOUR TRADING NEEDS**

Advanced automated trading system that monitors FUTURES charts and executes OPTIONS trades based on your exact technical analysis methodology.

## 🚀 Core Strategy

### **FUTURES ANALYSIS → OPTIONS TRADING**
- **Monitor**: NIFTY, BANKNIFTY, FINNIFTY (NSE) + SENSEX (BSE) futures charts
- **Analyze**: Your exact 6-factor signal system with RSI 21 OHLC4, MA 20/50, ADX 14
- **Trade**: Options contracts in the same month based on futures signals
- **Rollover**: Automatic rollover 7 days before expiry to avoid theta decay

### **Smart Instrument Handling**
- **NSE**: NIFTY, BANKNIFTY, FINNIFTY (via Kite Connect)
- **BSE**: SENSEX (via dedicated BSE fetcher)
- **Auto-detection**: Routes data requests to correct exchange

## 📊 Technical Analysis (Your Exact Setup)

### **Indicators**
- **RSI 21**: Calculated on OHLC4 source (O+H+L+C)/4
- **MA 20/50**: Simple moving averages for trend
- **ADX 14**: Trend strength confirmation
- **Linear Regression Slope 21H**: Momentum direction
- **Volume MA 20**: Volume confirmation

### **Signal Generation**
- **6-Factor Scoring**: Each condition scores 1 point
- **BUY/CALL Signal**: 4+ points + no RSI overbought
- **SELL/PUT Signal**: 4+ points + no RSI oversold
- **HOLD**: Mixed signals (< 4 points)

### **Strike Price Calculation**
- **NIFTY/FINNIFTY**: Round to nearest 50, +/- 50 for OTM
- **BANKNIFTY**: Round to nearest 100, +/- 100 for OTM  
- **SENSEX**: Round to nearest 100, +/- 100 for OTM

## 🛡️ Risk Management

- **Max Risk**: ₹2,000 per trade
- **Position Limit**: Maximum 3 simultaneous positions
- **Profit Target**: 15% gain
- **Stop Loss**: 8% loss
- **Auto Rollover**: 7 days before expiry (adjustable)

## � Quick Start

### **1. Environment Setup**
```bash
# Required for Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ID=your_chat_id

# Optional for live trading (simulation mode without these)
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_secret
KITE_ACCESS_TOKEN=your_access_token
```

### **2. Launch Bot**
```bash
# Simple launcher (recommended)
python launch_ultimate_bot.py

# Direct launch
python ultimate_sandy_sniper.py
```

### **3. Telegram Commands**
- `/start` - Start/resume trading
- `/status` - Check positions & current signals
- `/month` - Check current trading month
- `/stop` - Pause trading

## 📱 Live Trading Modes

### **Simulation Mode** (Default without Kite credentials)
- Paper trading with realistic price simulation
- Full strategy testing without real money
- Complete Telegram notifications

### **Live Mode** (With Kite Connect configured)
- Real money options trading
- Actual futures data analysis
- Live order execution

## 🔄 Auto Rollover Logic

```python
# Current logic: 7 days before expiry
if days_until_expiry <= 7:
    switch_to_next_month()
```

**Why 7 days?**
- Avoid theta decay acceleration
- Maintain liquidity
- Time to test and adjust

## 🎯 What Makes This Bot Special

### **✅ Your Exact Requirements**
1. **One robust bot** (not multiple versions)
2. **Futures monitoring** for chart analysis
3. **Options trading** based on futures signals
4. **Smart exchange routing** (BSE SENSEX + NSE others)
5. **Auto rollover** to avoid expiry risks
6. **Live trading** with real money execution

### **✅ Core Strategy Focus**
- Tests YOUR methodology first
- No premature optimizations
- Clean, focused implementation
- Real-time signal generation

## 📋 File Structure

```
ultimate_sandy_sniper.py    # Main bot (ONE ROBUST BOT)
launch_ultimate_bot.py      # Quick launcher
bse_sensex_fetcher.py       # BSE SENSEX data handler
live_trading_bot.py         # Original reference (can be archived)
```

## ⚠️ Important Notes

### **Testing Phase**
- Bot is designed to test your core strategy first
- Monitor signals and adjust rollover timing based on results
- Progressive enhancements after core validation

### **Data Sources**
- **SENSEX**: BSE (Yahoo Finance + BSE API fallbacks)
- **Others**: NSE via Kite Connect
- **Simulation**: Realistic sample data when APIs unavailable

## 🚀 Next Steps

1. **Launch in simulation mode** to verify signal generation
2. **Monitor telegram notifications** for strategy validation
3. **Adjust rollover timing** based on live results
4. **Enable live trading** when confident with signals
5. **Progressive enhancements** after core strategy proves effective

## 📞 Bot Commands Reference

```
/start    - Start the Ultimate Sandy Sniper Bot
/status   - View positions, signals, and bot health
/month    - Check current trading month & rollover status
/stop     - Pause all trading activities
```

---

**🎯 ONE BOT. YOUR STRATEGY. LIVE RESULTS.**

This is your **core strategy implementation** ready for live market testing. No assumptions, no premature optimizations - just your exact methodology automated and ready to generate real signals.
