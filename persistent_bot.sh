#!/bin/bash
"""
🚀 PERSISTENT BOT DEPLOYMENT SCRIPT
Keeps Sandy Sniper Bot running 24/7 even when you close browser/application
"""

echo "🚀 Setting up Persistent Sandy Sniper Bot Deployment"
echo "=" * 60

# Function to check if bot is running
check_bot_status() {
    if pgrep -f "ultimate_sandy_sniper_bot.py" > /dev/null; then
        echo "✅ Bot is running"
        return 0
    else
        echo "❌ Bot is not running"
        return 1
    fi
}

# Function to start bot in background
start_bot() {
    echo "🚀 Starting Ultimate Sandy Sniper Bot v5.0..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start bot with nohup (no hangup) to keep it running
    nohup python3 ultimate_sandy_sniper_bot.py > logs/bot_$(date +%Y%m%d_%H%M%S).log 2>&1 &
    
    # Get the process ID
    BOT_PID=$!
    echo "🎯 Bot started with PID: $BOT_PID"
    
    # Save PID to file for monitoring
    echo $BOT_PID > bot.pid
    
    # Wait a moment and check if it's running
    sleep 3
    if check_bot_status; then
        echo "✅ Bot is now running persistently in background"
        echo "📱 Test with /start in Telegram"
        echo "📋 Logs: logs/bot_$(date +%Y%m%d_%H%M%S).log"
    else
        echo "❌ Failed to start bot"
        exit 1
    fi
}

# Function to stop bot
stop_bot() {
    echo "🛑 Stopping bot..."
    if [ -f bot.pid ]; then
        PID=$(cat bot.pid)
        if kill $PID 2>/dev/null; then
            echo "✅ Bot stopped (PID: $PID)"
            rm bot.pid
        else
            echo "⚠️ Bot process not found, cleaning up PID file"
            rm bot.pid
        fi
    else
        # Try to kill by process name
        pkill -f "ultimate_sandy_sniper_bot.py"
        echo "✅ Bot processes terminated"
    fi
}

# Function to restart bot
restart_bot() {
    echo "🔄 Restarting bot..."
    stop_bot
    sleep 2
    start_bot
}

# Function to check bot health and auto-restart if needed
monitor_bot() {
    echo "👁️ Starting bot health monitor..."
    
    while true; do
        if ! check_bot_status; then
            echo "🚨 Bot not running! Auto-restarting..."
            start_bot
        else
            echo "✅ Bot health check passed - $(date)"
        fi
        
        # Check every 5 minutes
        sleep 300
    done
}

# Function to setup systemd service (for Linux servers)
setup_systemd_service() {
    echo "⚙️ Setting up systemd service for permanent deployment..."
    
    # Create service file
    sudo tee /etc/systemd/system/sandy-sniper-bot.service > /dev/null <<EOF
[Unit]
Description=Sandy Sniper Bot - Ultimate Trading Analysis
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 $(pwd)/ultimate_sandy_sniper_bot.py
Restart=always
RestartSec=10
StandardOutput=append:$(pwd)/logs/systemd_bot.log
StandardError=append:$(pwd)/logs/systemd_error.log

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable sandy-sniper-bot.service
    sudo systemctl start sandy-sniper-bot.service
    
    echo "✅ Systemd service created and started"
    echo "📋 Check status: sudo systemctl status sandy-sniper-bot"
    echo "📋 View logs: journalctl -u sandy-sniper-bot -f"
}

# Function to setup Docker deployment
setup_docker_deployment() {
    echo "🐳 Setting up Docker deployment..."
    
    # Create Dockerfile
    cat > Dockerfile <<EOF
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libta-lib0-dev \\
    sqlite3 \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ultimate_sandy_sniper_bot.py .
COPY .env .env

# Create directories
RUN mkdir -p logs data

# Set timezone
ENV TZ=Asia/Kolkata

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run bot
CMD ["python3", "ultimate_sandy_sniper_bot.py"]
EOF

    # Create docker-compose.yml
    cat > docker-compose.yml <<EOF
version: '3.8'

services:
  sandy-sniper-bot:
    build: .
    container_name: sandy-sniper-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=\${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_ID=\${TELEGRAM_ID}
      - KITE_API_KEY=\${KITE_API_KEY}
      - KITE_ACCESS_TOKEN=\${KITE_ACCESS_TOKEN}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./chat_history.db:/app/chat_history.db
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge

volumes:
  bot-logs:
  bot-data:
EOF

    echo "✅ Docker configuration created"
    echo "🚀 Start with: docker-compose up -d"
}

# Function to setup PM2 (Process Manager)
setup_pm2_deployment() {
    echo "⚡ Setting up PM2 process manager..."
    
    # Install PM2 if not present
    if ! command -v pm2 &> /dev/null; then
        echo "📦 Installing PM2..."
        npm install -g pm2
    fi
    
    # Create PM2 ecosystem file
    cat > ecosystem.config.js <<EOF
module.exports = {
  apps: [{
    name: 'sandy-sniper-bot',
    script: 'ultimate_sandy_sniper_bot.py',
    interpreter: 'python3',
    cwd: '$(pwd)',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    log_file: './logs/pm2_combined.log',
    out_file: './logs/pm2_out.log',
    error_file: './logs/pm2_error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
EOF

    # Start bot with PM2
    pm2 start ecosystem.config.js
    pm2 save
    pm2 startup
    
    echo "✅ PM2 deployment configured"
    echo "📋 Check status: pm2 status"
    echo "📋 View logs: pm2 logs sandy-sniper-bot"
    echo "📋 Monitor: pm2 monit"
}

# Function to create startup script for VS Code Codespaces
setup_codespaces_deployment() {
    echo "💻 Setting up VS Code Codespaces persistent deployment..."
    
    # Create startup script that runs on codespace start
    cat > .devcontainer/postCreateCommand.sh <<EOF
#!/bin/bash
echo "🚀 Auto-starting Sandy Sniper Bot in Codespace..."

# Install dependencies
pip install -r requirements.txt

# Start bot in background
cd /workspaces/Sandy_sniper-bot
nohup python3 ultimate_sandy_sniper_bot.py > logs/codespace_bot.log 2>&1 &

echo "✅ Bot started in Codespace"
echo "📱 Test with /start in Telegram"
EOF

    chmod +x .devcontainer/postCreateCommand.sh
    
    # Update devcontainer.json
    mkdir -p .devcontainer
    cat > .devcontainer/devcontainer.json <<EOF
{
    "name": "Sandy Sniper Bot Environment",
    "image": "mcr.microsoft.com/devcontainers/python:3.11",
    "features": {
        "ghcr.io/devcontainers/features/node:1": {
            "version": "18"
        }
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.pylint"
            ]
        }
    },
    "postCreateCommand": ".devcontainer/postCreateCommand.sh",
    "forwardPorts": [8000],
    "portsAttributes": {
        "8000": {
            "label": "Bot Health Check"
        }
    }
}
EOF

    echo "✅ Codespaces auto-start configured"
}

# Main menu
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        check_bot_status
        if [ -f bot.pid ]; then
            echo "📋 PID: $(cat bot.pid)"
        fi
        ;;
    monitor)
        monitor_bot
        ;;
    systemd)
        setup_systemd_service
        ;;
    docker)
        setup_docker_deployment
        ;;
    pm2)
        setup_pm2_deployment
        ;;
    codespaces)
        setup_codespaces_deployment
        ;;
    *)
        echo "🎯 Sandy Sniper Bot - Persistent Deployment Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|monitor|systemd|docker|pm2|codespaces}"
        echo ""
        echo "Commands:"
        echo "  start      - Start bot in background (survives browser close)"
        echo "  stop       - Stop the bot"
        echo "  restart    - Restart the bot"
        echo "  status     - Check if bot is running"
        echo "  monitor    - Start health monitor (auto-restart if needed)"
        echo "  systemd    - Setup Linux systemd service (permanent)"
        echo "  docker     - Setup Docker deployment"
        echo "  pm2        - Setup PM2 process manager"
        echo "  codespaces - Setup VS Code Codespaces auto-start"
        echo ""
        echo "🚀 For persistent deployment that survives browser close:"
        echo "   ./persistent_bot.sh start"
        echo ""
        echo "💡 For permanent server deployment:"
        echo "   ./persistent_bot.sh systemd"
        ;;
esac
