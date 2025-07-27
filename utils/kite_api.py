import os
from kiteconnect import KiteConnect
from utils.zerodha_auth import perform_auto_login  # Assumes this is your working login method

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

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite


# ✅ Place Order
def place_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    kite = get_kite_instance()
    try:
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
    kite = get_kite_instance()
    try:
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
