#!/bin/bash
# Run script for Sniper Swing Bot

echo "🤖 Starting Sniper Swing Bot..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "📝 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Validate setup first
echo "🔍 Validating setup..."
python validate_setup.py

if [ $? -eq 0 ]; then
    echo "✅ Setup validation passed!"
    echo "🚀 Starting bot..."
    
    # Run the main bot
    python main.py
else
    echo "❌ Setup validation failed!"
    echo "Please fix the issues before running the bot."
    exit 1
fi
