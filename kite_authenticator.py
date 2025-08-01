#!/usr/bin/env python3
"""
🔑 KITE CONNECT API AUTHENTICATION HELPER
Complete setup for live trading with Zerodha Kite Connect
"""

import os
import json
import webbrowser
from kiteconnect import KiteConnect
import pyotp

class KiteAuthenticator:
    def __init__(self):
        self.api_key = os.getenv('KITE_API_KEY')
        self.api_secret = os.getenv('KITE_API_SECRET')
        self.user_id = os.getenv('KITE_USER_ID')
        self.password = os.getenv('KITE_PASSWORD')
        self.totp_secret = os.getenv('KITE_TOTP_SECRET')
        
        if not all([self.api_key, self.api_secret]):
            raise ValueError("❌ Missing KITE_API_KEY or KITE_API_SECRET")
        
        self.kite = KiteConnect(api_key=self.api_key)
    
    def get_login_url(self):
        """Get Kite Connect login URL"""
        login_url = self.kite.login_url()
        print(f"🔗 Kite Login URL: {login_url}")
        
        # Try to open in browser
        try:
            webbrowser.open(login_url)
            print("✅ Opened login URL in browser")
        except:
            print("⚠️ Please manually open the URL above")
        
        return login_url
    
    def generate_totp(self):
        """Generate TOTP token"""
        if not self.totp_secret:
            print("❌ TOTP secret not configured")
            return None
        
        try:
            totp = pyotp.TOTP(self.totp_secret)
            token = totp.now()
            print(f"🔢 Current TOTP: {token}")
            return token
        except Exception as e:
            print(f"❌ TOTP generation failed: {e}")
            return None
    
    def authenticate_with_request_token(self, request_token):
        """Complete authentication with request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            access_token = data["access_token"]
            
            print(f"✅ Access Token: {access_token}")
            
            # Save to environment file
            self.save_access_token(access_token)
            
            # Test the connection
            self.kite.set_access_token(access_token)
            profile = self.kite.profile()
            
            print(f"✅ Authentication successful!")
            print(f"👤 User: {profile['user_name']}")
            print(f"📧 Email: {profile['email']}")
            print(f"💰 Broker: {profile['broker']}")
            
            return access_token
        
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return None
    
    def save_access_token(self, access_token):
        """Save access token to .env file"""
        try:
            # Read current .env
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add access token
            token_updated = False
            for i, line in enumerate(env_lines):
                if line.startswith('KITE_ACCESS_TOKEN='):
                    env_lines[i] = f'KITE_ACCESS_TOKEN={access_token}\n'
                    token_updated = True
                    break
            
            if not token_updated:
                env_lines.append(f'KITE_ACCESS_TOKEN={access_token}\n')
            
            # Write back to file
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            print("✅ Access token saved to .env file")
        
        except Exception as e:
            print(f"❌ Failed to save access token: {e}")
    
    def complete_authentication(self):
        """Complete authentication flow"""
        print("🔑 KITE CONNECT AUTHENTICATION")
        print("=" * 40)
        
        # Step 1: Get login URL
        login_url = self.get_login_url()
        
        # Step 2: Generate TOTP if available
        totp_token = self.generate_totp()
        if totp_token:
            print(f"🔢 Use this TOTP: {totp_token}")
        
        # Step 3: Get request token from user
        print("\n📋 STEPS:")
        print("1. Login to Kite using the URL above")
        print("2. Use your Zerodha credentials")
        if totp_token:
            print(f"3. Enter TOTP: {totp_token}")
        print("4. After login, copy the 'request_token' from the URL")
        print("5. Paste it below")
        
        request_token = input("\n🔑 Enter request token: ").strip()
        
        if request_token:
            access_token = self.authenticate_with_request_token(request_token)
            if access_token:
                print("\n🎉 AUTHENTICATION COMPLETE!")
                print("Your bot can now trade with live money!")
                return True
        
        print("\n❌ Authentication failed")
        return False

def main():
    """Main authentication function"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        authenticator = KiteAuthenticator()
        success = authenticator.complete_authentication()
        
        if success:
            print("\n🚀 Ready for live trading!")
            print("Run: python3 live_trading_bot.py")
        else:
            print("\n❌ Setup incomplete")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
