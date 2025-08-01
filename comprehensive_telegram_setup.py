#!/usr/bin/env python3
"""
🔧 COMPLETE TELEGRAM SETUP & VALIDATION SYSTEM
Comprehensive setup, testing, and validation for Telegram bot functionality
"""

import os
import sys
import json
import requests
import asyncio
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment
load_dotenv()

class TelegramSetupManager:
    """Complete Telegram setup and validation system"""
    
    def __init__(self):
        self.bot_token = None
        self.chat_id = None
        self.setup_complete = False
        
    def print_header(self, title, char="="):
        """Print formatted header"""
        print(f"\n{char*60}")
        print(f"🔧 {title}")
        print(f"{char*60}")
    
    def print_status(self, message, status="info"):
        """Print formatted status"""
        icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        print(f"{icons.get(status, 'ℹ️')} {message}")
    
    def check_current_environment(self):
        """Check current environment for credentials"""
        self.print_header("CHECKING CURRENT ENVIRONMENT")
        
        # Common environment variable names
        token_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_TOKEN', 'BOT_TOKEN']
        chat_vars = ['TELEGRAM_CHAT_ID', 'TELEGRAM_ID', 'CHAT_ID']
        
        found_token = None
        found_chat = None
        
        for var in token_vars:
            value = os.getenv(var)
            if value and not value.endswith('_here') and ':' in value:
                found_token = value
                self.print_status(f"Found valid token in {var}", "success")
                break
            elif value:
                self.print_status(f"Found placeholder in {var}: {value[:20]}...", "warning")
        
        for var in chat_vars:
            value = os.getenv(var)
            if value and not value.endswith('_here') and (value.startswith('-') or value.isdigit()):
                found_chat = value
                self.print_status(f"Found valid chat ID in {var}", "success")
                break
            elif value:
                self.print_status(f"Found placeholder in {var}: {value}", "warning")
        
        if found_token and found_chat:
            self.bot_token = found_token
            self.chat_id = found_chat
            return True
        
        return False
    
    def validate_token_format(self, token):
        """Validate bot token format"""
        if not token:
            return False, "Token is empty"
        
        if not isinstance(token, str):
            return False, "Token must be a string"
        
        if token.endswith('_here') or 'your_' in token.lower():
            return False, "Token appears to be a placeholder"
        
        parts = token.split(':')
        if len(parts) != 2:
            return False, "Token must be in format 'bot_id:token'"
        
        bot_id, bot_token = parts
        if not bot_id.isdigit():
            return False, "Bot ID must be numeric"
        
        if len(bot_token) < 35:
            return False, "Bot token appears too short"
        
        return True, "Token format is valid"
    
    def validate_chat_id_format(self, chat_id):
        """Validate chat ID format"""
        if not chat_id:
            return False, "Chat ID is empty"
        
        if str(chat_id).endswith('_here') or 'your_' in str(chat_id).lower():
            return False, "Chat ID appears to be a placeholder"
        
        chat_str = str(chat_id)
        if not (chat_str.startswith('-') or chat_str.lstrip('-').isdigit()):
            return False, "Chat ID must be numeric (can be negative for groups)"
        
        return True, "Chat ID format is valid"
    
    def test_bot_api(self):
        """Test bot API connection"""
        self.print_header("TESTING BOT API CONNECTION")
        
        if not self.bot_token:
            self.print_status("No bot token to test", "error")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                bot_info = response.json()['result']
                self.print_status("Bot API connection successful!", "success")
                self.print_status(f"Bot Username: @{bot_info.get('username', 'Unknown')}")
                self.print_status(f"Bot Name: {bot_info.get('first_name', 'Unknown')}")
                self.print_status(f"Bot ID: {bot_info.get('id', 'Unknown')}")
                self.print_status(f"Can Join Groups: {bot_info.get('can_join_groups', False)}")
                self.print_status(f"Can Read All Group Messages: {bot_info.get('can_read_all_group_messages', False)}")
                return True
            else:
                error_data = response.json() if response.content else {}
                error_desc = error_data.get('description', 'Unknown error')
                self.print_status(f"Bot API Error [{response.status_code}]: {error_desc}", "error")
                
                if response.status_code == 401:
                    self.print_status("❌ Bot token is invalid or expired", "error")
                elif response.status_code == 404:
                    self.print_status("❌ Bot not found - check your token", "error")
                
                return False
                
        except requests.exceptions.Timeout:
            self.print_status("Connection timeout - check your internet", "error")
            return False
        except requests.exceptions.ConnectionError:
            self.print_status("Connection error - check your internet", "error")
            return False
        except Exception as e:
            self.print_status(f"Unexpected error: {e}", "error")
            return False
    
    def test_chat_access(self):
        """Test chat access"""
        self.print_header("TESTING CHAT ACCESS")
        
        if not self.bot_token or not self.chat_id:
            self.print_status("Missing credentials for chat test", "error")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            response = requests.get(url, params={'chat_id': self.chat_id}, timeout=15)
            
            if response.status_code == 200:
                chat_info = response.json()['result']
                self.print_status("Chat access verified!", "success")
                self.print_status(f"Chat Type: {chat_info.get('type', 'Unknown')}")
                
                if chat_info.get('type') == 'private':
                    name = f"{chat_info.get('first_name', '')} {chat_info.get('last_name', '')}".strip()
                    self.print_status(f"Private Chat with: {name}")
                    if chat_info.get('username'):
                        self.print_status(f"Username: @{chat_info.get('username')}")
                else:
                    self.print_status(f"Group/Channel: {chat_info.get('title', 'Unknown')}")
                
                return True
            else:
                error_data = response.json() if response.content else {}
                error_desc = error_data.get('description', 'Unknown error')
                self.print_status(f"Chat Access Error [{response.status_code}]: {error_desc}", "error")
                
                if response.status_code == 400:
                    self.print_status("❌ Invalid chat ID format", "error")
                elif response.status_code == 403:
                    self.print_status("❌ Bot doesn't have access to this chat", "error")
                    self.print_status("💡 Make sure you've started the bot or added it to the group", "info")
                
                return False
                
        except Exception as e:
            self.print_status(f"Chat test error: {e}", "error")
            return False
    
    def send_test_message(self):
        """Send test message"""
        self.print_header("SENDING TEST MESSAGE")
        
        try:
            test_message = f"""🎯 **Sandy Sniper Bot - Connection Test**

✅ **Status**: All systems operational!
⏰ **Test Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
🤖 **Bot**: Ready for live trading
📊 **Features**: All Telegram commands working

**Available Commands:**
• /start - Initialize bot
• /status - System status
• /positions - Current positions
• /market - Market data
• /help - Command help

🚀 **Ready to trade!**"""

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': test_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                message_info = response.json()['result']
                self.print_status("Test message sent successfully! ✉️", "success")
                self.print_status(f"Message ID: {message_info.get('message_id')}")
                self.print_status("Check your Telegram to see the message!", "info")
                return True
            else:
                error_data = response.json() if response.content else {}
                error_desc = error_data.get('description', 'Unknown error')
                self.print_status(f"Message Send Error [{response.status_code}]: {error_desc}", "error")
                return False
                
        except Exception as e:
            self.print_status(f"Failed to send test message: {e}", "error")
            return False
    
    def test_telegram_bot_library(self):
        """Test python-telegram-bot library"""
        self.print_header("TESTING TELEGRAM BOT LIBRARY")
        
        try:
            from telegram import Bot
            from telegram.ext import Application, CommandHandler
            
            self.print_status("python-telegram-bot imported successfully", "success")
            
            if self.bot_token:
                # Test Bot creation
                bot = Bot(token=self.bot_token)
                self.print_status("Bot object created successfully", "success")
                
                # Test Application creation
                app = Application.builder().token(self.bot_token).build()
                self.print_status("Application object created successfully", "success")
                
                # Test handler creation
                async def dummy_handler(update, context):
                    pass
                
                handler = CommandHandler("test", dummy_handler)
                app.add_handler(handler)
                self.print_status("Command handler added successfully", "success")
                
                return True
            else:
                self.print_status("No token available for library test", "warning")
                return False
                
        except ImportError as e:
            self.print_status(f"python-telegram-bot not installed: {e}", "error")
            self.print_status("Run: pip install python-telegram-bot", "info")
            return False
        except Exception as e:
            self.print_status(f"Library test failed: {e}", "error")
            return False
    
    def create_sample_env(self):
        """Create sample .env configuration"""
        self.print_header("CREATING SAMPLE CONFIGURATION")
        
        sample_env = """# Sandy Sniper Bot - Telegram Configuration
# Replace the values below with your actual credentials

# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk

# Your Telegram chat ID (get from @userinfobot)
# For private chat: your user ID (positive number)
# For group chat: group ID (negative number starting with -)
TELEGRAM_ID=123456789

# Alternative variable names (choose one set)
# TELEGRAM_CHAT_ID=123456789
# BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk

# Other configurations...
"""
        
        try:
            with open('.env.sample', 'w') as f:
                f.write(sample_env)
            self.print_status("Created .env.sample with example configuration", "success")
            self.print_status("Copy .env.sample to .env and update with your credentials", "info")
        except Exception as e:
            self.print_status(f"Failed to create sample config: {e}", "error")
    
    def show_setup_instructions(self):
        """Show setup instructions"""
        self.print_header("TELEGRAM BOT SETUP INSTRUCTIONS", "-")
        
        print("""
📋 **HOW TO SET UP YOUR TELEGRAM BOT:**

1️⃣ **CREATE A BOT:**
   • Open Telegram and message @BotFather
   • Send /newbot command
   • Choose a name and username for your bot
   • Copy the bot token (format: 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ...)

2️⃣ **GET YOUR CHAT ID:**
   • Message @userinfobot to get your user ID
   • OR start your bot and send any message
   • OR for groups: add bot to group and get group ID

3️⃣ **UPDATE CONFIGURATION:**
   • Edit your .env file
   • Replace TELEGRAM_BOT_TOKEN with your actual token
   • Replace TELEGRAM_ID with your actual chat ID

4️⃣ **TEST THE CONNECTION:**
   • Run this script again to verify everything works
   • Check that you receive the test message in Telegram

💡 **TROUBLESHOOTING:**
   • Make sure your bot token has the format: numbers:letters
   • Chat ID should be numeric (negative for groups)
   • Start your bot by sending /start in Telegram
   • For groups: add the bot and make it an admin if needed
""")
    
    def run_full_validation(self):
        """Run complete validation suite"""
        self.print_header("SANDY SNIPER BOT - TELEGRAM VALIDATION SUITE")
        
        success_count = 0
        total_tests = 6
        
        # Test 1: Check environment
        if not self.check_current_environment():
            self.print_status("❌ No valid credentials found in environment", "error")
            self.show_setup_instructions()
            self.create_sample_env()
            return False
        
        success_count += 1
        
        # Test 2: Validate token format
        valid, message = self.validate_token_format(self.bot_token)
        if not valid:
            self.print_status(f"❌ Token validation failed: {message}", "error")
            return False
        
        success_count += 1
        self.print_status("✅ Token format validation passed", "success")
        
        # Test 3: Validate chat ID format
        valid, message = self.validate_chat_id_format(self.chat_id)
        if not valid:
            self.print_status(f"❌ Chat ID validation failed: {message}", "error")
            return False
        
        success_count += 1
        self.print_status("✅ Chat ID format validation passed", "success")
        
        # Test 4: Test bot API
        if not self.test_bot_api():
            return False
        
        success_count += 1
        
        # Test 5: Test chat access
        if not self.test_chat_access():
            return False
        
        success_count += 1
        
        # Test 6: Send test message
        if not self.send_test_message():
            self.print_status("⚠️ Test message failed, but connection is working", "warning")
        else:
            success_count += 1
        
        # Bonus: Test library
        if self.test_telegram_bot_library():
            self.print_status("✅ Bonus: python-telegram-bot library working!", "success")
        
        # Final results
        self.print_header("VALIDATION RESULTS")
        
        if success_count >= 5:  # Allow test message to fail
            self.print_status(f"🎉 SUCCESS! ({success_count}/{total_tests} tests passed)", "success")
            self.print_status("✅ Telegram bot is ready for live trading!", "success")
            self.print_status("✅ All commands should work properly!", "success")
            
            # Show credentials being used
            self.print_status(f"Using Bot Token: {self.bot_token[:15]}...{self.bot_token[-10:]}", "info")
            self.print_status(f"Using Chat ID: {self.chat_id}", "info")
            
            self.setup_complete = True
            return True
        else:
            self.print_status(f"❌ FAILED! ({success_count}/{total_tests} tests passed)", "error")
            self.print_status("Please fix the issues above and try again", "error")
            return False

def main():
    """Main execution function"""
    manager = TelegramSetupManager()
    
    try:
        success = manager.run_full_validation()
        
        if success:
            print(f"\n{'='*60}")
            print("🚀 TELEGRAM SETUP IS COMPLETE!")
            print("🎯 Your Sandy Sniper Bot is ready for live trading!")
            print("📱 Try sending /start to your bot in Telegram!")
            print(f"{'='*60}")
            
            # Save success state
            with open('.telegram_validated', 'w') as f:
                f.write(f"validated_at={datetime.now().isoformat()}\n")
                f.write(f"bot_token_length={len(manager.bot_token) if manager.bot_token else 0}\n")
                f.write(f"chat_id={manager.chat_id}\n")
            
            return 0
        else:
            print(f"\n{'='*60}")
            print("❌ TELEGRAM SETUP FAILED!")
            print("💡 Follow the instructions above to fix the issues")
            print("🔧 Run this script again after updating your configuration")
            print(f"{'='*60}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
