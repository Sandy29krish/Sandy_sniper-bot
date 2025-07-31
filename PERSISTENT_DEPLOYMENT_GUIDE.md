# 🚀 Persistent Bot Deployment Guide

**Keep your Sandy Sniper Bot running 24/7 even when you close browser/application**

## 🎯 Quick Start (Recommended)

### Option 1: VS Code Codespaces (Easiest)
```bash
# Your bot will auto-start when Codespace opens
# Just ensure .env is configured with your credentials
# Bot runs persistently in background even when browser is closed
```

### Option 2: Simple Background Process
```bash
# Start bot in background (survives browser close)
./persistent_bot.sh start

# Check if running
./persistent_bot.sh status

# Stop if needed
./persistent_bot.sh stop
```

## 🏗️ Deployment Options

### 1. 💻 VS Code Codespaces (Auto-Start)
**Perfect for: Development and testing**

✅ **Automatic Setup:**
- Bot auto-starts when Codespace opens
- Runs in background even when browser is closed
- Auto-restarts on Codespace resume

```bash
# Configuration is already done in .devcontainer/
# Just ensure your .env file has correct credentials:
TELEGRAM_BOT_TOKEN=your_actual_token
TELEGRAM_ID=your_actual_chat_id
```

### 2. 🔄 Background Process (nohup)
**Perfect for: Simple persistent deployment**

```bash
# Start bot persistently
./persistent_bot.sh start

# Monitor health (auto-restart if crashes)
./persistent_bot.sh monitor

# Check status anytime
./persistent_bot.sh status
```

### 3. 🐳 Docker Deployment (Production)
**Perfect for: Server deployment with full isolation**

```bash
# Setup Docker configuration
./persistent_bot.sh docker

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f sandy-sniper-bot

# Stop
docker-compose down
```

### 4. ⚡ PM2 Process Manager
**Perfect for: Advanced process management**

```bash
# Setup PM2 deployment
./persistent_bot.sh pm2

# Monitor processes
pm2 monit

# View logs
pm2 logs sandy-sniper-bot
```

### 5. 🖥️ Linux Systemd Service
**Perfect for: Permanent server installation**

```bash
# Setup system service (requires sudo)
./persistent_bot.sh systemd

# Check status
sudo systemctl status sandy-sniper-bot

# View logs
journalctl -u sandy-sniper-bot -f
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required for bot operation
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ID=your_telegram_chat_id

# Optional for live data
KITE_API_KEY=your_zerodha_api_key
KITE_ACCESS_TOKEN=your_zerodha_access_token

# Bot settings
AUTO_ROLLOVER=true
ROLLOVER_DAYS=7
THETA_PROTECTION=true
```

## 📱 Usage After Deployment

Once deployed persistently, your bot will:

✅ **Run 24/7** - Even when you close browser/application  
✅ **Auto-restart** - If it crashes or server reboots  
✅ **Keep chat history** - Across all devices and sessions  
✅ **Handle rollover** - Automatically without intervention  
✅ **Send alerts** - Real-time Telegram notifications  

### Test Commands:
```bash
/start      # Bot responds immediately
/analysis   # Get real-time analysis
/history    # See persistent chat history
/rollover   # Check auto-rollover status
```

## 🛠️ Troubleshooting

### Bot Not Responding?
```bash
# Check if running
./persistent_bot.sh status

# Check logs
tail -f logs/bot_*.log

# Restart if needed
./persistent_bot.sh restart
```

### Docker Issues?
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs sandy-sniper-bot

# Restart container
docker-compose restart sandy-sniper-bot
```

### Codespace Issues?
```bash
# Check if autostart script ran
cat logs/codespace_*.log

# Manual start if needed
bash .devcontainer/autostart.sh
```

## 🎯 Deployment Comparison

| Method | Persistence | Auto-Restart | Ease | Best For |
|--------|-------------|--------------|------|----------|
| Codespaces | ✅ | ✅ | 🟢 Easy | Development |
| Background | ✅ | ⚠️ Manual | 🟢 Easy | Quick setup |
| Docker | ✅ | ✅ | 🟡 Medium | Production |
| PM2 | ✅ | ✅ | 🟡 Medium | Advanced |
| Systemd | ✅ | ✅ | 🔴 Complex | Servers |

## 🚀 Recommended Deployment Flow

### For Development/Testing:
1. **Use VS Code Codespaces** - Auto-starts, easy to manage
2. **Configure .env** with your credentials
3. **Test with /start** in Telegram

### For Production:
1. **Use Docker Compose** for isolation and reliability
2. **Setup monitoring** with health checks
3. **Configure auto-updates** with Watchtower

### For Personal Server:
1. **Use Systemd service** for permanent installation
2. **Setup log rotation** for maintenance
3. **Configure firewall** for security

## 🎉 Success Indicators

✅ **Bot Running**: `./persistent_bot.sh status` shows "Bot is running"  
✅ **Telegram Responsive**: `/start` command gets immediate response  
✅ **Logs Active**: New entries in `logs/` directory  
✅ **Cross-Device**: Chat history works on all devices  
✅ **Auto-Features**: Rollover monitoring active  

---

**🎯 Your Sandy Sniper Bot is now running persistently 24/7!**

*Choose the deployment method that best fits your needs. The bot will continue running even when you close your browser or application.*
