import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv
from utils.zerodha_auth import perform_auto_login  # Assumes this is your working login method

# Load environment variables
load_dotenv()

# 🔁 This function will be called by all modules to get a working kite instance
def get_kite_instance():
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")

    if not api_key:
        raise Exception("❌ KITE_API_KEY is missing from environment variables.")

    if not access_token:
        print("⚠️ ACCESS_TOKEN not found in environment. Attempting auto-login...")
        access_token = perform_auto_login()  # Auto-login using TOTP
        if not access_token:
            raise Exception("❌ Auto-login failed. Could not get access token.")
        # Update environment variable for future use
        os.environ["KITE_ACCESS_TOKEN"] = access_token

    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        
        # Test the connection by making a simple API call
        try:
            profile = kite.profile()
            print(f"✅ Kite connection successful for user: {profile.get('user_name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Warning: Could not verify Kite connection: {e}")
            # Continue anyway, the connection might still work for trading
            
        return kite
    except Exception as e:
        raise Exception(f"❌ Failed to create Kite instance: {e}")


# ✅ Place Order
def place_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    if not tradingsymbol or not exchange:
        print("❌ Invalid trading symbol or exchange")
        return None
        
    try:
        kite = get_kite_instance()
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type
        )
        print(f"✅ Order placed: {order_id}")
        return order_id
    except Exception as e:
        print(f"❌ Order placement failed: {e}")
        return None


# ✅ Exit Order
def exit_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    if not tradingsymbol or not exchange:
        print("❌ Invalid trading symbol or exchange")
        return None
        
    try:
        kite = get_kite_instance()
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type
        )
        print(f"✅ Exit order placed: {order_id}")
        return order_id
    except Exception as e:
        print(f"❌ Exit order failed: {e}")
        return None
