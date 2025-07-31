#!/bin/bash
echo "🔧 Setting up Sandy Sniper Bot environment..."

# Install system dependencies for TA-Lib
sudo apt-get update
sudo apt-get install -y build-essential libta-lib0-dev sqlite3

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs data

# Set up environment template if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "📝 Created .env file from template - please configure your credentials"
fi

echo "✅ Environment setup complete!"
