from kiteconnect import KiteConnect
import os
import logging

API_KEY = os.getenv("ZERODHA_API_KEY")
API_SECRET = os.getenv("ZERODHA_API_SECRET")
ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

def place_order(instrument_token, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=None,  # Use instrument_token
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type,
            instrument_token=instrument_token
        )
        logging.info(f"Order placed. ID: {order_id}")
        return order_id
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        raise

def exit_order(instrument_token, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=None,
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type,
            instrument_token=instrument_token
        )
        logging.info(f"Exit order placed. ID: {order_id}")
        return order_id
    except Exception as e:
        logging.error(f"Error placing exit order: {e}")
        raise
