# utils/kite_api.py

from kiteconnect import KiteConnect
import os
import logging

API_KEY = os.getenv("KITE_API_KEY")
API_SECRET = os.getenv("KITE_API_SECRET")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

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
        logging.info(f"Order placed. ID: {order_id}")
        return order_id
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        raise

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
        logging.info(f"Exit order placed. ID: {order_id}")
        return order_id
    except Exception as e:
        logging.error(f"Error placing exit order: {e}")
        raise
