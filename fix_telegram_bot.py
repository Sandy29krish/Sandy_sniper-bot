#!/usr/bin/env python3
"""
🔧 TELEGRAM BOT FIX - Complete Setup Guide
Creates a new working Telegram bot for Sandy Sniper Bot
"""

import requests
import json

def test_token(token):
    """Test if a token is valid"""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            return True, bot_info
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def get_chat_id_from_updates(token):
    """Get chat ID from recent messages"""
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            updates = response.json()['result']
            if updates:
                # Get the most recent message
                latest_update = updates[-1]
                chat = latest_update.get('message', {}).get('chat', {})
                return chat.get('id'), chat.get('first_name', 'User')
            else:
                return None, "No messages found - send a message to your bot first"
        return None, f"API Error: {response.text}"
    except Exception as e:
        return None, str(e)

def main():
    print("🤖 TELEGRAM BOT FIX WIZARD")
    print("=" * 50)
    
    print("\n📋 STEP 1: CREATE A NEW BOT")
    print("-" * 30)
    print("1. Open Telegram and search for 'BotFather'")
    print("2. Send /newbot to BotFather")
    print("3. Choose a name: 'Sandy Sniper Bot'")
    print("4. Choose a username: 'SandySniperBot' (or similar)")
    print("5. Copy the bot token that BotFather gives you")
    
    print("\n🔑 STEP 2: ENTER YOUR NEW BOT TOKEN")
    print("-" * 30)
    
    while True:
        token = input("Enter your bot token: ").strip()
        
        if not token:
            print("❌ Please enter a valid token")
            continue
            
        if ':' not in token:
            print("❌ Invalid token format. Should contain ':'")
            continue
            
        print(f"\n🧪 Testing token: {token[:15]}...")
        
        valid, result = test_token(token)
        
        if valid:
            bot_info = result
            print(f"✅ Bot token is VALID!")
            print(f"   Bot Name: {bot_info.get('first_name', 'Unknown')}")
            print(f"   Bot Username: @{bot_info.get('username', 'Unknown')}")
            print(f"   Bot ID: {bot_info.get('id', 'Unknown')}")
            break
        else:
            print(f"❌ Token is invalid: {result}")
            print("Please check and enter the correct token")
    
    print("\n💬 STEP 3: GET YOUR CHAT ID")
    print("-" * 30)
    print("1. Open your new bot in Telegram")
    print("2. Send /start to your bot")
    print("3. Send any message (like 'hello')")
    
    input("\nPress Enter after you've sent messages to your bot...")
    
    print("\n🔍 Getting your chat ID...")
    chat_id, name = get_chat_id_from_updates(token)
    
    if chat_id:
        print(f"✅ Found your chat ID: {chat_id}")
        print(f"   User: {name}")
        
        # Test sending a message
        print("\n📤 Testing message sending...")
        test_message = """🎉 TELEGRAM BOT FIXED!

✅ Connection: Working perfectly
🤖 Bot: Sandy Sniper Bot
👤 User: Connected
⏰ Time: Working

🚀 Ready for live trading commands!"""
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': test_message
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Test message sent successfully!")
            print("📱 Check your Telegram - you should see the test message")
            
            # Update .env file
            print("\n📝 UPDATING .ENV FILE...")
            
            # Read current .env
            try:
                with open('.env', 'r') as f:
                    content = f.read()
                
                # Update the tokens
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    if line.startswith('TELEGRAM_BOT_TOKEN='):
                        new_lines.append(f'TELEGRAM_BOT_TOKEN={token}')
                    elif line.startswith('TELEGRAM_ID='):
                        new_lines.append(f'TELEGRAM_ID={chat_id}')
                    else:
                        new_lines.append(line)
                
                # Write updated .env
                with open('.env', 'w') as f:
                    f.write('\n'.join(new_lines))
                
                print("✅ .env file updated successfully!")
                
            except Exception as e:
                print(f"⚠️ Could not update .env file: {e}")
                print(f"\nPlease manually update your .env file:")
                print(f"TELEGRAM_BOT_TOKEN={token}")
                print(f"TELEGRAM_ID={chat_id}")
                
        else:
            print(f"❌ Test message failed: {response.text}")
            
    else:
        print(f"❌ Could not get chat ID: {name}")
        print("Please make sure you sent messages to your bot")
    
    print("\n" + "=" * 50)
    print("🎯 TELEGRAM BOT SETUP COMPLETE!")
    print("🚀 Your bot should now respond to commands!")
    print("=" * 50)

if __name__ == "__main__":
    main()
