#!/usr/bin/env python3
"""
🔧 Kite Authentication Fix
Implement direct token authentication to avoid Chrome browser conflicts
"""

import os
import logging
from kiteconnect import KiteConnect

def fix_kite_authentication():
    """
    Fix Kite API authentication by using direct token approach
    Bypass Chrome automation to resolve session conflicts
    """
    
    print("🔧 FIXING KITE API AUTHENTICATION")
    print("=" * 50)
    
    # Get secrets from environment
    api_key = os.getenv('KITE_API_KEY')
    api_secret = os.getenv('KITE_API_SECRET')
    access_token = os.getenv('KITE_ACCESS_TOKEN')
    
    if not api_key:
        print("❌ KITE_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key: {api_key[:15]}...")
    
    # Try direct token authentication
    if access_token:
        print("🔑 Testing existing access token...")
        try:
            kite = KiteConnect(api_key=api_key)
            kite.set_access_token(access_token)
            
            # Test with a simple API call
            profile = kite.profile()
            if profile:
                print(f"✅ Token VALID - User: {profile.get('user_name', 'Unknown')}")
                print(f"✅ Broker: {profile.get('broker', 'Unknown')}")
                print(f"✅ Email: {profile.get('email', 'Unknown')}")
                
                # Update the GitHub secrets token file
                with open("/tmp/kite_token_working.txt", "w") as f:
                    f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
                    f.write(f"API_KEY={api_key}\n")
                    f.write(f"STATUS=WORKING\n")
                
                return True
                
        except Exception as e:
            print(f"❌ Access token invalid: {e}")
    
    # Manual token generation guide
    print("\n" + "=" * 50)
    print("🔑 MANUAL TOKEN GENERATION REQUIRED")
    print("=" * 50)
    
    if api_key and api_secret:
        kite = KiteConnect(api_key=api_key)
        login_url = kite.login_url()
        
        print(f"📋 Step 1: Visit this URL: {login_url}")
        print("📋 Step 2: Login with your Zerodha credentials")
        print("📋 Step 3: After login success, copy the 'request_token' from URL")
        print("📋 Step 4: Run the token generator with that request_token")
        print("\n💡 Once you get the request_token, I can generate the access_token")
        
    else:
        print("❌ API_SECRET missing - cannot generate login URL")
        print("💡 Please add KITE_API_SECRET to GitHub secrets")
    
    return False

def generate_access_token_from_request_token(request_token: str):
    """Generate access token from request token"""
    
    api_key = os.getenv('KITE_API_KEY')
    api_secret = os.getenv('KITE_API_SECRET')
    
    if not all([api_key, api_secret, request_token]):
        print("❌ Missing required parameters for token generation")
        return None
    
    try:
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        print(f"✅ Access token generated: {access_token[:20]}...")
        
        # Save to file
        with open("/tmp/new_access_token.txt", "w") as f:
            f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return None

if __name__ == "__main__":
    success = fix_kite_authentication()
    
    if not success:
        print("\n🔧 ALTERNATIVE SOLUTIONS:")
        print("1. Update KITE_ACCESS_TOKEN in GitHub secrets with fresh token")
        print("2. Add KITE_API_SECRET for automatic token generation") 
        print("3. Use manual browser login to get request_token")
        print("\n💡 System will continue with FALLBACK mode until fixed")
