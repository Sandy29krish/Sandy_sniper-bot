from kiteconnect import KiteConnect
import os
import logging

API_KEY = os.getenv("KITE_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

# Global kite instance
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ✅ Needed by indicators.py and other modules
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
