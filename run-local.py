#!/usr/bin/env python3
"""
Local Development Runner for Trading Bot

This script helps you run the trading bot locally while reminding you about
proper security practices for production deployment.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Check if environment is properly set up for local development."""
    print("🔍 Checking local development environment...")
    
    # Load environment variables
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\n📋 To set up local development:")
        print("1. Copy env.template to .env")
        print("2. Fill in your development credentials")
        print("3. Run this script again")
        print("\n⚠️  IMPORTANT: Never commit .env files with real credentials!")
        return False
    
    load_dotenv()
    
    # Check required variables
    required_vars = [
        'KITE_API_KEY',
        'KITE_API_SECRET', 
        'KITE_USER_ID',
        'KITE_PASSWORD',
        'KITE_TOTP_SECRET'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value.startswith('your_') and value.endswith('_here'):
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    if placeholder_vars:
        print(f"⚠️  Placeholder values detected: {', '.join(placeholder_vars)}")
        print("Please update these with your actual credentials.")
        return False
    
    print("✅ Local environment setup looks good!")
    return True

def show_security_reminder():
    """Show security reminders for production deployment."""
    print("\n" + "="*60)
    print("🔒 SECURITY REMINDER FOR PRODUCTION")
    print("="*60)
    print("For production deployment, use GitHub Secrets instead of .env files:")
    print("")
    print("1. 🌐 Go to your GitHub repository settings")
    print("2. 🔐 Navigate to Secrets and variables → Actions") 
    print("3. ➕ Add all your credentials as repository secrets")
    print("4. 🚀 Use GitHub Actions workflows for secure deployment")
    print("")
    print("📖 See setup-github-secrets.md for detailed instructions")
    print("="*60)

def main():
    """Main function to run the trading bot locally."""
    print("🤖 Trading Bot - Local Development Runner")
    print("="*50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Show security reminder
    show_security_reminder()
    
    # Ask for confirmation
    print("\n❓ Do you want to run the bot locally? (y/n): ", end="")
    response = input().lower().strip()
    
    if response != 'y':
        print("👋 Exiting. Use GitHub Actions for production deployment!")
        sys.exit(0)
    
    print("\n🚀 Starting trading bot locally...")
    print("💡 Tip: Use Ctrl+C to stop the bot\n")
    
    try:
        # Import and run the main bot
        from main import main as run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()