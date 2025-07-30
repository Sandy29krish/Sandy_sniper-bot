import os
import time
from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException, NetworkException, TokenException, OrderException
from dotenv import load_dotenv
from utils.zerodha_auth import perform_auto_login  # Assumes this is your working login method

# Load environment variables
load_dotenv()

# Custom exceptions for better error handling
class KiteConnectionError(Exception):
    """Custom exception for Kite connection issues"""
    pass

class KiteOrderError(Exception):
    """Custom exception for order placement issues"""
    pass

class KiteDataError(Exception):
    """Custom exception for data fetching issues"""
    pass

def retry_on_failure(max_retries=3, delay=2):
    """Decorator for retrying functions on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (NetworkException, ConnectionError, TimeoutError) as e:
                    if attempt == max_retries - 1:
                        raise KiteConnectionError(f"Network error after {max_retries} attempts: {e}")
                    print(f"⚠️ Network error on attempt {attempt + 1}/{max_retries}: {e}")
                    time.sleep(delay * (attempt + 1))
                except TokenException as e:
                    print(f"🔐 Token expired, attempting refresh...")
                    access_token = perform_auto_login()
                    if access_token:
                        os.environ["KITE_ACCESS_TOKEN"] = access_token
                        if attempt == max_retries - 1:
                            raise KiteConnectionError(f"Token refresh failed after {max_retries} attempts")
                        continue
                    else:
                        raise KiteConnectionError(f"Failed to refresh token: {e}")
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"⚠️ Error on attempt {attempt + 1}/{max_retries}: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# 🔁 This function will be called by all modules to get a working kite instance
@retry_on_failure(max_retries=3, delay=1)
def get_kite_instance():
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")

    if not api_key:
        raise KiteConnectionError("❌ KITE_API_KEY is missing from environment variables.")

    if not access_token:
        print("⚠️ ACCESS_TOKEN not found in environment. Attempting auto-login...")
        access_token = perform_auto_login()  # Auto-login using TOTP
        if not access_token:
            raise KiteConnectionError("❌ Auto-login failed. Could not get access token.")
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
        raise KiteConnectionError(f"❌ Failed to create Kite instance: {e}")


# ✅ Place Order with enhanced error handling
@retry_on_failure(max_retries=3, delay=1)
def place_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    if not tradingsymbol or not exchange:
        raise KiteOrderError("❌ Invalid trading symbol or exchange")
        
    if quantity <= 0:
        raise KiteOrderError("❌ Invalid quantity: must be greater than 0")
        
    valid_transaction_types = ["BUY", "SELL"]
    if transaction_type not in valid_transaction_types:
        raise KiteOrderError(f"❌ Invalid transaction type: {transaction_type}. Must be one of {valid_transaction_types}")
        
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
        print(f"✅ Order placed successfully: {order_id} | {tradingsymbol} | {transaction_type} | Qty: {quantity}")
        return order_id
    except OrderException as e:
        raise KiteOrderError(f"❌ Order placement failed - Order error: {e}")
    except KiteException as e:
        raise KiteOrderError(f"❌ Order placement failed - Kite API error: {e}")
    except Exception as e:
        raise KiteOrderError(f"❌ Order placement failed - Unexpected error: {e}")


# ✅ Exit Order with enhanced error handling
@retry_on_failure(max_retries=3, delay=1)
def exit_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    if not tradingsymbol or not exchange:
        raise KiteOrderError("❌ Invalid trading symbol or exchange for exit order")
        
    if quantity <= 0:
        raise KiteOrderError("❌ Invalid exit quantity: must be greater than 0")
        
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
        print(f"✅ Exit order placed successfully: {order_id} | {tradingsymbol} | {transaction_type} | Qty: {quantity}")
        return order_id
    except OrderException as e:
        raise KiteOrderError(f"❌ Exit order failed - Order error: {e}")
    except KiteException as e:
        raise KiteOrderError(f"❌ Exit order failed - Kite API error: {e}")
    except Exception as e:
        raise KiteOrderError(f"❌ Exit order failed - Unexpected error: {e}")

# 📊 Get positions with error handling
@retry_on_failure(max_retries=2, delay=1)
def get_positions():
    """Get current positions with enhanced error handling"""
    try:
        kite = get_kite_instance()
        positions = kite.positions()
        return positions
    except KiteException as e:
        raise KiteDataError(f"❌ Failed to fetch positions: {e}")
    except Exception as e:
        raise KiteDataError(f"❌ Unexpected error fetching positions: {e}")

# 📈 Get LTP with error handling
@retry_on_failure(max_retries=2, delay=1)
def get_ltp(instrument_tokens):
    """Get Last Traded Price with enhanced error handling"""
    try:
        kite = get_kite_instance()
        if isinstance(instrument_tokens, (str, int)):
            instrument_tokens = [instrument_tokens]
        
        ltp_data = kite.ltp(instrument_tokens)
        return ltp_data
    except KiteException as e:
        raise KiteDataError(f"❌ Failed to fetch LTP: {e}")
    except Exception as e:
        raise KiteDataError(f"❌ Unexpected error fetching LTP: {e}")
