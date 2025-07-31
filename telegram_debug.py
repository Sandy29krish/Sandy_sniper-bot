#!/usr/bin/env python3
"""
🔧 Telegram Debug Test
Direct test with your correct credentials
"""

import requests
import json
import pytz
import os
from datetime import datetime

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current Indian Standard Time"""
    return datetime.now(IST)

def test_telegram_direct():
    """Direct Telegram API test with your credentials"""
    
    from dotenv import load_dotenv
    load_dotenv('/workspaces/Sandy_sniper-bot/.env')
    
    # Load from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_ID')
    
    if not bot_token or not chat_id:
        print("❌ Error: Could not load credentials from .env")
        return False
    
    print("🧪 TELEGRAM DEBUG TEST")
    print("=" * 50)
    print(f"Bot Token: {bot_token[:15]}...")
    print(f"Chat ID: {chat_id}")
    
    try:
        # Step 1: Test bot info
        print("\n🤖 Step 1: Testing Bot Info...")
        bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(bot_url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"   ✅ Bot Username: @{bot_info.get('username', 'Unknown')}")
            print(f"   ✅ Bot Name: {bot_info.get('first_name', 'Unknown')}")
            print(f"   ✅ Bot ID: {bot_info.get('id', 'Unknown')}")
        else:
            print(f"   ❌ Bot API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Step 2: Test chat access
        print("\n💬 Step 2: Testing Chat Access...")
        chat_url = f"https://api.telegram.org/bot{bot_token}/getChat"
        chat_response = requests.get(chat_url, params={'chat_id': chat_id}, timeout=10)
        
        if chat_response.status_code == 200:
            chat_info = chat_response.json()['result']
            print(f"   ✅ Chat Type: {chat_info.get('type', 'Unknown')}")
            print(f"   ✅ Chat ID: {chat_info.get('id', 'Unknown')}")
            if chat_info.get('username'):
                print(f"   ✅ Username: @{chat_info.get('username')}")
            if chat_info.get('first_name'):
                print(f"   ✅ Name: {chat_info.get('first_name')}")
        else:
            print(f"   ❌ Chat API Error: {chat_response.status_code}")
            print(f"   Response: {chat_response.text}")
            print("   💡 This might be the issue - bot can't access your chat")
            return False
        
        # Step 3: Send test message
        print("\n📤 Step 3: Sending Test Message...")
        
        test_message = f"""🎉 TELEGRAM TEST MESSAGE

✅ Connection Status: SUCCESS
📅 Time: {get_indian_time().strftime('%Y-%m-%d %H:%M:%S IST')}
🤖 Bot: @{bot_info.get('username', 'Unknown')}
💬 Chat: {chat_info.get('type', 'Unknown')}

🚀 Sandy Sniper Bot is LIVE!
📊 Ready for Zerodha chart analysis
🔧 All systems operational"""
        
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': test_message
        }
        
        send_response = requests.post(send_url, json=payload, timeout=10)
        
        if send_response.status_code == 200:
            result = send_response.json()['result']
            print(f"   ✅ Message sent successfully!")
            print(f"   📧 Message ID: {result.get('message_id', 'Unknown')}")
            ist_time = datetime.fromtimestamp(result.get('date', 0), tz=IST)
            print(f"   📅 Sent at: {ist_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            print(f"   💬 Chat ID confirmed: {result.get('chat', {}).get('id', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Send Error: {send_response.status_code}")
            print(f"   Response: {send_response.text}")
            
            # Common error analysis
            if send_response.status_code == 400:
                print("   💡 Error 400: Bad Request - Check chat_id format")
            elif send_response.status_code == 403:
                print("   💡 Error 403: Forbidden - Bot blocked or haven't started bot")
                print("   🔧 Solution: Send /start to your bot first")
            elif send_response.status_code == 404:
                print("   💡 Error 404: Not Found - Invalid bot token or chat_id")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔍 TROUBLESHOOTING TELEGRAM CONNECTION...")
    
    success = test_telegram_direct()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 TELEGRAM TEST: SUCCESS! ✅")
        print("📱 Check your Telegram app for the test message")
        print("🔔 Make sure notifications are enabled")
    else:
        print("❌ TELEGRAM TEST: FAILED!")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Open Telegram and search for your bot")
        print("2. Send /start to activate the bot")
        print("3. Check if bot is blocked or muted")
        print("4. Verify the chat_id is your personal user ID")
        print("5. Make sure bot token is complete and correct")
    print("=" * 50)

if __name__ == "__main__":
    main()
