#!/usr/bin/env python3
"""
Simple Telegram Test for Sandy Sniper Bot
"""

import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_telegram():
    """Test Telegram bot connection"""
    print("🧪 SIMPLE TELEGRAM TEST")
    print("=" * 40)
    
    # Get credentials
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_ID')
    
    print(f"Token: {token[:15] if token else 'None'}...")
    print(f"Chat ID: {chat_id}")
    
    if not token or not chat_id:
        print("❌ Missing credentials in .env file")
        return False
    
    try:
        # Test 1: Bot info
        print("\n🤖 Testing bot info...")
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        response = requests.get(url, timeout=15)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Bot: @{bot_info.get('username', 'unknown')}")
            
            # Test 2: Send message
            print("\n📤 Sending test message...")
            
            message = """🎯 TELEGRAM TEST SUCCESS!

✅ Sandy Sniper Bot is connected
⏰ Commands should work now
🚀 Ready for live trading!

Try these commands:
/start - Start the bot
/status - System status
/help - Show commands"""
            
            send_url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            
            send_response = requests.post(send_url, json=payload, timeout=15)
            
            if send_response.status_code == 200:
                print("✅ Message sent successfully!")
                print("📱 Check your Telegram app!")
                return True
            else:
                print(f"❌ Send failed: {send_response.status_code}")
                print(f"Error: {send_response.text}")
                return False
                
        else:
            print(f"❌ Bot test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_telegram()
    
    if success:
        print("\n🎉 TELEGRAM IS WORKING!")
        print("Your bot should now respond to commands!")
    else:
        print("\n❌ TELEGRAM TEST FAILED")
        print("Check your internet connection and credentials")
