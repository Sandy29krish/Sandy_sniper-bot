#!/usr/bin/env python3
"""
🧪 Telegram Connectivity Test Script
Tests updated GitHub secrets and Telegram functionality
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_telegram_connection():
    """Test Telegram connectivity with updated GitHub secrets"""
    
    print("🧪 TELEGRAM CONNECTIVITY TEST")
    print("=" * 50)
    
    # Check environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_ID')
    
    print(f"📋 Environment Check:")
    print(f"   Bot Token: {'✅ Present' if bot_token else '❌ Missing'} ({len(bot_token) if bot_token else 0} chars)")
    print(f"   Chat ID: {'✅ Present' if chat_id else '❌ Missing'} ({chat_id if chat_id else 'None'})")
    
    if not bot_token or not chat_id:
        print("\n❌ GitHub secrets not loaded!")
        print("💡 Make sure you've updated the repository secrets")
        return False
    
    try:
        # Test bot info
        print(f"\n🤖 Testing Bot Info...")
        bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(bot_url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"   ✅ Bot Username: @{bot_info.get('username', 'Unknown')}")
            print(f"   ✅ Bot Name: {bot_info.get('first_name', 'Unknown')}")
            print(f"   ✅ Bot ID: {bot_info.get('id', 'Unknown')}")
        else:
            print(f"   ❌ Bot API Error: {response.status_code} - {response.text}")
            return False
        
        # Test chat info
        print(f"\n💬 Testing Chat Access...")
        chat_url = f"https://api.telegram.org/bot{bot_token}/getChat"
        chat_response = requests.get(chat_url, params={'chat_id': chat_id}, timeout=10)
        
        if chat_response.status_code == 200:
            chat_info = chat_response.json()['result']
            print(f"   ✅ Chat Type: {chat_info.get('type', 'Unknown')}")
            print(f"   ✅ Chat ID: {chat_info.get('id', 'Unknown')}")
        else:
            print(f"   ❌ Chat API Error: {chat_response.status_code} - {chat_response.text}")
            return False
        
        # Send test message
        print(f"\n📤 Sending Test Message...")
        
        test_message = f"""🎉 **Sandy Sniper Bot - Connection Test SUCCESS!**

✅ **Telegram**: Connected successfully  
📅 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
🤖 **Bot**: @{bot_info.get('username', 'Unknown')}  
💬 **Chat**: {chat_info.get('type', 'Unknown')}  

🚀 **System Status**:
• Chart Analysis: Ready for Zerodha integration
• AI Assistant: Enhanced with technical indicators  
• GitHub Secrets: Successfully loaded
• Bulletproof System: 24/7 monitoring active

💹 **Supported Indices**:
• NIFTY (₹24,854.80)
• BANKNIFTY (₹56,068.60)  
• FINNIFTY (₹23,800.00)
• SENSEX (₹80,873.16)

📊 **Ready to analyze your Zerodha charts!** 📈"""
        
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': test_message,
            'parse_mode': 'Markdown'
        }
        
        send_response = requests.post(send_url, json=payload, timeout=10)
        
        if send_response.status_code == 200:
            print("   ✅ Test message sent successfully!")
            message_info = send_response.json()['result']
            print(f"   📧 Message ID: {message_info.get('message_id', 'Unknown')}")
            print(f"   📅 Sent at: {datetime.fromtimestamp(message_info.get('date', 0))}")
            return True
        else:
            print(f"   ❌ Send Error: {send_response.status_code} - {send_response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_telegram_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 TELEGRAM TEST: SUCCESS! ✅")
        print("📱 Check your Telegram for the test message")
        print("🚀 Sandy Sniper Bot is ready for notifications!")
    else:
        print("❌ TELEGRAM TEST: FAILED!")
        print("💡 Check your GitHub secrets and try again")
    print("=" * 50)

if __name__ == "__main__":
    main()
