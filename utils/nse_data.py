# utils/nse_data.py

import logging

def get_future_price(symbol):
    """
    Mock function to return future price. Replace with real API logic if needed.
    """
    future_prices = {
        "NIFTY": 17650,
        "BANKNIFTY": 42600,
        "SENSEX": 73500,
    }
    price = future_prices.get(symbol.upper(), 0)
    logging.info(f"[get_future_price] Returning mocked price for {symbol}: {price}")
    return price


def get_next_expiry_date(symbol):
    """
    Mock function to return next expiry date for the given symbol.
    Replace with actual NSE option chain or Zerodha API logic.
    """
    from datetime import datetime, timedelta
    today = datetime.today()
    expiry = today + timedelta((3 - today.weekday()) % 7)  # Next Thursday logic
    return expiry.strftime('%Y-%m-%d')
