
# 🎯 Sniper Swing Bot

**Advanced AI-Powered Options Trading Bot for Indian Markets**

An intelligent trading bot that automatically executes swing trades on NIFTY, BANKNIFTY, SENSEX, and FINNIFTY based on sophisticated technical analysis and AI-driven decision making.

## 🚀 Features

### Core Trading Features
- **Multi-Symbol Trading**: NIFTY, BANKNIFTY, SENSEX, FINNIFTY
- **Advanced Technical Analysis**: RSI, Moving Averages, Linear Regression, CPR levels
- **AI-Powered Signals**: Machine learning for trade entry/exit decisions
- **Signal Strength Analysis**: Ranks trading opportunities by strength (7.0+ threshold)
- **Dynamic Position Sizing**: Intelligent lot calculation based on available capital
- **Risk Management**: Max daily trades, position limits, stop-loss automation

### Exit Strategy Features
- **Swing High/Low Detection**: Partial profit booking at swing points
- **15-Min SMA Cross**: Technical exit signals
- **Volume Divergence Detection**: Exit on volume drops
- **Linear Regression Slope**: Trend reversal detection
- **AI Momentum Analysis**: Sentiment-based exit timing

### Advanced Features
- **Gap Handler**: Automatic gap-up/gap-down scenario management
- **Auto Rollover**: Seamless options contract rollover management
- **Friday 3:15 PM Auto-Exit**: Automated position closure
- **Intelligent Order Management**: Smart order execution with retry logic
- **Real-time Monitoring**: Live position tracking and P&L calculation

### System Features
- **Health Monitoring**: CPU, memory, disk, network monitoring
- **Telegram Integration**: Real-time alerts and remote control
- **Enhanced Logging**: Detailed trade logs with AI reasoning
- **Watchdog Protection**: Automatic error recovery and alerts
- **Enhanced Scheduler**: Market-aware timing management

## 📦 Quick Setup

### 1. Automated Installation
```bash
# Clone the repository
git clone https://github.com/Sandy29krish/Sandy_sniper-bot.git
cd Sandy_sniper-bot

# Run automated installation
./install.sh
```

### 2. Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.template .env
```

### 3. Configuration
Edit `.env` file with your credentials:
```bash
# Zerodha/Kite API
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_USER_ID=your_user_id
KITE_PASSWORD=your_password
KITE_TOTP_SECRET=your_totp_secret

# Telegram (optional but recommended)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ID=your_chat_id

# Trading
CAPITAL=170000
```

### 4. Validation & Run
```bash
# Validate setup
python validate_setup.py

# Run the bot
./run.sh
# OR
python main.py
```

## 🎛️ Configuration

### Trading Parameters
- **Capital**: ₹170,000 default (adjustable)
- **Max Daily Trades**: 3
- **Max Simultaneous Positions**: 3
- **Risk Per Trade**: 33% of capital
- **Signal Strength Threshold**: 7.0/10

### Symbols Configuration
```python
SYMBOLS = {
    'NIFTY': {'lot_size': 75, 'exchange': 'NSE'},
    'BANKNIFTY': {'lot_size': 30, 'exchange': 'NSE'},
    'SENSEX': {'lot_size': 10, 'exchange': 'BSE'},
    'FINNIFTY': {'lot_size': 40, 'exchange': 'NSE'}
}
```

## 📊 Signal Analysis

The bot uses a sophisticated 7-component signal strength analyzer:

1. **Trend Alignment** (25%): MA hierarchy, LR slope, price position
2. **Momentum Strength** (20%): RSI, MACD, Stochastic alignment  
3. **Volume Confirmation** (15%): PVI, volume trends, spikes
4. **Support/Resistance** (15%): CPR levels, Bollinger Bands
5. **RSI Position** (10%): Optimal RSI zones for entry
6. **MA Confluence** (10%): Moving average alignment
7. **Volatility Factor** (5%): ATR-based volatility assessment

### Signal Grades
- **SUPER_STRONG**: 9.0+ (Highest priority)
- **VERY_STRONG**: 8.0-8.9 (High priority)
- **STRONG**: 7.0-7.9 (Trade threshold)
- **MODERATE**: 5.0-6.9 (Monitor only)
- **WEAK**: Below 5.0 (Ignore)

## 🔄 Trading Workflow

1. **Market Analysis**: Scans all symbols every 60 seconds
2. **Signal Generation**: Calculates technical indicators
3. **Strength Ranking**: Ranks signals by strength score
4. **Position Entry**: Executes top-ranked signals (7.0+)
5. **Position Monitoring**: Continuous exit condition checking
6. **Exit Management**: Partial/full exits based on conditions
7. **Risk Management**: Daily/position limits enforcement

## 🛡️ Risk Management

### Position Limits
- Maximum 3 trades per day
- Maximum 3 simultaneous positions
- 33% capital allocation per trade
- Maximum 5 lots per position

### Exit Conditions
- **Immediate**: Friday 3:15 PM, gap scenarios
- **Technical**: 15-min SMA cross, volume drop
- **AI-Based**: Momentum weakness detection
- **Profit**: Swing high partial exits

### Safety Features
- Automatic error recovery
- Connection health monitoring  
- Order execution validation
- Real-time P&L tracking

## 📱 Telegram Integration

### Commands
- `/start` - Initialize bot interaction
- `/status` - Get current bot status
- `/positions` - View active positions
- `/help` - Show available commands

### Notifications
- Trade entries with AI reasoning
- Exit alerts with P&L details
- System health warnings
- Error notifications

## 📈 Performance Monitoring

### Real-time Metrics
- Active positions count
- Daily trade count
- Current P&L
- System resource usage
- Market status

### Logging
- Trade execution logs
- Error tracking
- Performance metrics
- AI decision reasoning

## 🔧 Advanced Usage

### Production Deployment
For production environments, use GitHub Secrets instead of `.env` files:

1. Go to Repository Settings → Secrets and variables → Actions
2. Add required secrets (see `setup-github-secrets.md`)
3. Use GitHub Actions for automated deployment

### Custom Configuration
Edit `config.yaml` for advanced settings:
```yaml
trading:
  capital: 170000
  max_daily_trades: 3
  risk_per_trade: 0.33

signal_analysis:
  minimum_strength: 7.0
  confidence_threshold: "MEDIUM"
```

### Running in Background
```bash
# Using tmux
tmux new-session -d -s trading-bot './run.sh'

# Using nohup
nohup python main.py > trading.log 2>&1 &

# Using systemd (Linux)
sudo systemctl start sniper-bot
```

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install -r requirements.txt
python validate_setup.py
```

**API Connection Issues**
- Check Kite API credentials
- Verify TOTP secret
- Test connection: `python -c "from utils.kite_api import test_connection; test_connection()"`

**Telegram Not Working**
- Verify bot token and chat ID
- Test: `python -c "from telegram_commands import test_telegram_connection; print(test_telegram_connection())"`

**Market Data Issues**
- Check NSE connectivity
- Verify symbol mappings
- Test: `python -c "from utils.nse_data import get_future_price; print(get_future_price('NIFTY'))"`

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

### Health Checks
```bash
# System health
python -c "from system_health_monitor import get_system_health_summary; print(get_system_health_summary())"

# Validate all components
python validate_setup.py
```

## 📚 Documentation

- `setup-github-secrets.md` - GitHub Secrets setup
- `env.template` - Environment variables reference
- `config.yaml` - Configuration options
- Individual module documentation in `utils/` directory

## ⚠️ Disclaimers

- **Educational Purpose**: This bot is for educational and research purposes
- **Risk Warning**: Trading involves substantial risk of loss
- **No Guarantees**: Past performance doesn't guarantee future results
- **Test First**: Always test in paper trading mode first
- **Compliance**: Ensure compliance with local trading regulations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Report security issues privately

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⚡ Happy Trading! ⚡**

*Made with ❤️ for the trading community*
