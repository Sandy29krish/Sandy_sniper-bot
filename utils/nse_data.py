# utils/nse_data.py

import logging
from datetime import datetime, timedelta

def get_future_price(symbol):
    future_prices = {
        "NIFTY": 17650,
        "BANKNIFTY": 42600,
        "SENSEX": 73500,
    }
    price = future_prices.get(symbol.upper(), 0)
    logging.info(f"[get_future_price] Returning mocked price for {symbol}: {price}")
    return price

def get_next_expiry_date(symbol):
    today = datetime.today()
    expiry = today + timedelta((3 - today.weekday()) % 7)  # Next Thursday logic
    return expiry.strftime('%Y-%m-%d')

# ✅ Add this mapping at the end
SYMBOL_TOKEN_MAP = {
    "NIFTY": 256265,
    "BANKNIFTY": 260105,
    "SENSEX": 265,
    "FINNIFTY": 111111
}
