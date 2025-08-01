# 🚀 LIVE TRADING SETUP GUIDE

## STEP 1: Get Zerodha Kite Connect API Access

### 📱 Create Kite Connect App:
1. Go to: https://kite.trade/
2. Click "Get Started" 
3. Login with your Zerodha credentials
4. Go to "My Apps" → "Create App"
5. Fill details:
   - App Name: `Sandy Sniper Bot`
   - Description: `Automated trading bot`
   - Redirect URL: `http://127.0.0.1:8000/`
   - Post-back URL: (leave blank)

### 🔑 Get API Credentials:
After creating the app, you'll get:
- **API Key** (Consumer Key)
- **API Secret** (Consumer Secret)

## STEP 2: Configure Your Bot

### 📝 Edit .env file:
```bash
# Replace these with your actual Zerodha credentials
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_USER_ID=your_zerodha_user_id
KITE_PASSWORD=your_zerodha_password
KITE_TOTP_SECRET=your_totp_secret_from_zerodha_app
```

### 🔐 Setup TOTP (2FA):
1. In Zerodha Kite app, go to Settings → Security
2. Enable TOTP and scan QR code
3. Save the secret key (not the 6-digit codes)
4. Put the secret in `KITE_TOTP_SECRET`

## STEP 3: Authenticate and Start Trading

### 🔑 First-time Authentication:
```bash
# Install required packages
pip install kiteconnect pyotp

# Run authentication
python3 kite_authenticator.py
```

### 🚀 Start Live Trading:
```bash
# Start the live trading bot
./start_persistent.sh
```

## ⚡ TRADING FEATURES

### 💰 Risk Management:
- **Max Risk**: ₹2,000 per trade
- **Min Lot Size**: 1 lot
- **Max Positions**: 3 at once
- **Profit Target**: 15%
- **Stop Loss**: 8%

### 📊 Trading Strategy:
- **Indicators**: RSI(21), MA(20,50), ADX(14)
- **Timeframe**: 5-minute charts
- **Markets**: NIFTY Futures primarily
- **Hours**: 9:15 AM - 3:30 PM IST

### 📱 Telegram Commands:
- `/start` - Activate bot
- `/status` - Check positions
- `/balance` - View account balance
- `/stop_trading` - Pause trading
- `/resume_trading` - Resume trading

## ⚠️ IMPORTANT NOTES

### 🔒 Security:
- Keep your API credentials secret
- Never share your .env file
- Use strong passwords
- Enable all Zerodha security features

### 💸 Risk Warning:
- **This bot trades with REAL MONEY**
- Start with small amounts
- Monitor your positions
- Understand the risks involved
- Only trade what you can afford to lose

### 📈 Performance:
- Bot analyzes markets every minute
- Places trades based on exact indicators
- Automatically manages stop-losses
- Sends trade notifications to Telegram

## 🚀 READY TO TRADE!

Once authenticated, your bot will:
1. ✅ Connect to live markets
2. ✅ Analyze price movements 
3. ✅ Place automatic trades
4. ✅ Manage positions with stops
5. ✅ Send you trade alerts

**Your Sandy Sniper Bot will be fully automated and trading live!**
