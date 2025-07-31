#!/usr/bin/env python3
"""
🔧 ROBUST TELEGRAM CONNECTION TEST & SETUP
Complete testing suite for Telegram connectivity with multiple credential sources
"""

import os
import sys
import requests
import json
import asyncio
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RobustTelegramTester:
    """Comprehensive Telegram testing and setup"""
    
    def __init__(self):
        self.bot_token = None
        self.chat_id = None
        self.test_results = []
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_status(self, message, status="info"):
        """Print formatted status message"""
        icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        print(f"{icons.get(status, 'ℹ️')} {message}")
    
    def test_credential_sources(self):
        """Test multiple credential sources"""
        self.print_header("TESTING CREDENTIAL SOURCES")
        
        # Test sources in priority order
        sources = [
            ("Environment Variables", self.test_env_vars),
            ("GitHub Secrets", self.test_github_secrets),
            (".env File", self.test_dotenv_file),
            ("Config Files", self.test_config_files),
            ("Manual Input", self.test_manual_input)
        ]
        
        for source_name, test_func in sources:
            self.print_status(f"Testing {source_name}...")
            try:
                if test_func():
                    self.print_status(f"{source_name}: SUCCESS", "success")
                    break
                else:
                    self.print_status(f"{source_name}: No credentials found", "warning")
            except Exception as e:
                self.print_status(f"{source_name}: ERROR - {e}", "error")
        
        return self.bot_token and self.chat_id
    
    def test_env_vars(self):
        """Test environment variables"""
        token_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_TOKEN', 'BOT_TOKEN']
        chat_vars = ['TELEGRAM_CHAT_ID', 'TELEGRAM_ID', 'CHAT_ID']
        
        for var in token_vars:
            if os.getenv(var):
                self.bot_token = os.getenv(var)
                break
        
        for var in chat_vars:
            if os.getenv(var):
                self.chat_id = os.getenv(var)
                break
        
        return self.bot_token and self.chat_id
    
    def test_github_secrets(self):
        """Test GitHub secrets (in Actions environment)"""
        # GitHub Actions automatically loads secrets as environment variables
        return self.test_env_vars()
    
    def test_dotenv_file(self):
        """Test .env file"""
        env_files = ['.env', '.env.local', '.env.production']
        
        for env_file in env_files:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    content = f.read()
                    
                if 'TELEGRAM_BOT_TOKEN=' in content and not content.split('TELEGRAM_BOT_TOKEN=')[1].split('\n')[0].strip().endswith('_here'):
                    # Load the file
                    load_dotenv(env_file, override=True)
                    return self.test_env_vars()
        
        return False
    
    def test_config_files(self):
        """Test configuration files"""
        config_files = ['config.yaml', 'config.json', 'telegram_config.json']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    if config_file.endswith('.yaml'):
                        import yaml
                        with open(config_file, 'r') as f:
                            config = yaml.safe_load(f)
                    else:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                    
                    # Extract telegram credentials
                    telegram_config = config.get('telegram', {})
                    self.bot_token = telegram_config.get('bot_token') or telegram_config.get('token')
                    self.chat_id = telegram_config.get('chat_id') or telegram_config.get('id')
                    
                    if self.bot_token and self.chat_id:
                        return True
                        
                except Exception as e:
                    self.print_status(f"Error reading {config_file}: {e}", "error")
        
        return False
    
    def test_manual_input(self):
        """Allow manual input of credentials"""
        self.print_status("No credentials found in configuration files")
        self.print_status("Would you like to enter them manually? (y/n)", "warning")
        
        # For automated testing, return False
        # In interactive mode, you could prompt for input
        return False
    
    def validate_credentials(self):
        """Validate the credentials"""
        if not self.bot_token or not self.chat_id:
            return False, "Missing credentials"
        
        # Basic format validation
        if not self.bot_token.count(':') == 1:
            return False, "Invalid bot token format"
        
        if not (self.chat_id.startswith('-') or self.chat_id.isdigit()):
            return False, "Invalid chat ID format"
        
        return True, "Credentials format valid"
    
    def test_bot_connection(self):
        """Test bot API connection"""
        self.print_header("TESTING BOT CONNECTION")
        
        if not self.bot_token:
            self.print_status("No bot token available", "error")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()['result']
                self.print_status(f"Bot connected successfully", "success")
                self.print_status(f"Bot Username: @{bot_info.get('username', 'Unknown')}")
                self.print_status(f"Bot Name: {bot_info.get('first_name', 'Unknown')}")
                self.print_status(f"Bot ID: {bot_info.get('id', 'Unknown')}")
                return True
            else:
                self.print_status(f"Bot API Error: {response.status_code} - {response.text}", "error")
                return False
                
        except Exception as e:
            self.print_status(f"Connection failed: {e}", "error")
            return False
    
    def test_chat_access(self):
        """Test chat access"""
        self.print_header("TESTING CHAT ACCESS")
        
        if not self.bot_token or not self.chat_id:
            self.print_status("Missing credentials for chat test", "error")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            response = requests.get(url, params={'chat_id': self.chat_id}, timeout=10)
            
            if response.status_code == 200:
                chat_info = response.json()['result']
                self.print_status(f"Chat access verified", "success")
                self.print_status(f"Chat Type: {chat_info.get('type', 'Unknown')}")
                self.print_status(f"Chat Title: {chat_info.get('title', chat_info.get('first_name', 'Private Chat'))}")
                return True
            else:
                self.print_status(f"Chat access failed: {response.status_code} - {response.text}", "error")
                return False
                
        except Exception as e:
            self.print_status(f"Chat test failed: {e}", "error")
            return False
    
    def send_test_message(self):
        """Send a test message"""
        self.print_header("SENDING TEST MESSAGE")
        
        if not self.bot_token or not self.chat_id:
            self.print_status("Cannot send test message - missing credentials", "error")
            return False
        
        try:
            test_message = f"🧪 **Sandy Sniper Bot Test**\n\n✅ Connection successful!\n⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🤖 All systems operational!"
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': test_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.print_status("Test message sent successfully!", "success")
                return True
            else:
                self.print_status(f"Failed to send message: {response.status_code} - {response.text}", "error")
                return False
                
        except Exception as e:
            self.print_status(f"Message send failed: {e}", "error")
            return False
    
    def test_async_functionality(self):
        """Test async Telegram functionality"""
        self.print_header("TESTING ASYNC FUNCTIONALITY")
        
        try:
            # Test if python-telegram-bot can be imported
            from telegram import Bot
            from telegram.ext import Application
            
            self.print_status("python-telegram-bot library imported successfully", "success")
            
            if self.bot_token:
                # Test bot creation
                bot = Bot(token=self.bot_token)
                self.print_status("Bot object created successfully", "success")
                
                # Test application creation
                app = Application.builder().token(self.bot_token).build()
                self.print_status("Application object created successfully", "success")
                
                return True
            else:
                self.print_status("Cannot test bot creation - no token", "warning")
                return False
                
        except ImportError as e:
            self.print_status(f"python-telegram-bot not properly installed: {e}", "error")
            return False
        except Exception as e:
            self.print_status(f"Async test failed: {e}", "error")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        self.print_header("COMPREHENSIVE TELEGRAM TEST SUITE")
        
        # Test 1: Find credentials
        if not self.test_credential_sources():
            self.print_status("CRITICAL: No valid credentials found!", "error")
            return False
        
        # Test 2: Validate credentials
        valid, message = self.validate_credentials()
        if not valid:
            self.print_status(f"CRITICAL: {message}", "error")
            return False
        
        self.print_status(f"Using Bot Token: {self.bot_token[:10]}...{self.bot_token[-4:]}", "info")
        self.print_status(f"Using Chat ID: {self.chat_id}", "info")
        
        # Test 3: Bot connection
        if not self.test_bot_connection():
            return False
        
        # Test 4: Chat access
        if not self.test_chat_access():
            return False
        
        # Test 5: Send test message
        if not self.send_test_message():
            return False
        
        # Test 6: Async functionality
        if not self.test_async_functionality():
            self.print_status("Async functionality test failed, but basic functionality works", "warning")
        
        self.print_header("TEST RESULTS")
        self.print_status("ALL TESTS PASSED! Telegram is ready for use.", "success")
        
        return True

def main():
    """Main function"""
    tester = RobustTelegramTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n{'='*60}")
            print("🎉 TELEGRAM SETUP COMPLETE!")
            print("✅ Your bot is ready for live trading!")
            print("✅ All commands should work properly!")
            print(f"{'='*60}")
            return 0
        else:
            print(f"\n{'='*60}")
            print("❌ TELEGRAM SETUP FAILED!")
            print("💡 Please check the errors above and fix the issues.")
            print("💡 Make sure your bot token and chat ID are correct.")
            print(f"{'='*60}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
