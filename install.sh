#!/bin/bash
# Installation script for Sniper Swing Bot

echo "🚀 Installing Sniper Swing Bot Dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install TA-Lib (may require additional system dependencies)
echo "📈 Installing TA-Lib..."
pip install TA-Lib

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env file with your actual credentials"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x run.sh 2>/dev/null || true

echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Test the setup: python validate_setup.py"
echo "3. Run the bot: python main.py"
echo ""
echo "🔧 For production, use GitHub Secrets instead of .env file"
echo "   See setup-github-secrets.md for details"
