from kiteconnect import KiteConnect
import os
import logging

def read_access_token_from_file():
    """Reads the latest access token from file"""
    token_file = "/root/.kite_token_env"
    try:
        with open(token_file, "r") as f:
            for line in f:
                if "KITE_ACCESS_TOKEN" in line:
                    return line.strip().split("=")[1]
    except Exception as e:
        logging.error(f"❌ Failed to read access token from file: {e}")
    return None

# ✅ Use file-based token loading
API_KEY = os.getenv("KITE_API_KEY")
ACCESS_TOKEN = read_access_token_from_file()

kite = KiteConnect(api_key=API_KEY)

if ACCESS_TOKEN:
    kite.set_access_token(ACCESS_TOKEN)
else:
    logging.warning("⚠️ ACCESS_TOKEN not found. Token might not be set yet.")

# ✅ Shared instance
def get_kite_instance():
    return kite

# ✅ Order placement
def place_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
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
        logging.info(f"✅ Order placed: {order_id}")
        return order_id
    except Exception as e:
        logging.error(f"❌ Failed to place order: {e}")
        raise

# ✅ Exit order
def exit_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
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
        logging.info(f"✅ Exit order placed: {order_id}")
        return order_id
    except Exception as e:
        logging.error(f"❌ Failed to exit order: {e}")
        raise
