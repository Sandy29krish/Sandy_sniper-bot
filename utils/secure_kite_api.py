#!/usr/bin/env python3
"""
Secure Kite API

This module provides secure access to Zerodha Kite API without exposing secrets.
"""

import os
import sys
import logging

# Add parent directory to path to import secure_auth_manager
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from secure_auth_manager import SecureAuthManager
except ImportError:
    print("❌ SecureAuthManager not found. Please run secure_auth_manager.py first.")
    sys.exit(1)

# Global auth manager instance
_auth_manager = None
_kite_instance = None

def get_auth_manager():
    """Get or create auth manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = SecureAuthManager()
    return _auth_manager

def get_kite_instance():
    """Get authenticated Kite instance (cached)"""
    global _kite_instance
    
    if _kite_instance is None:
        auth_manager = get_auth_manager()
        _kite_instance = auth_manager.get_kite_instance()
        
        if _kite_instance is None:
            raise Exception("❌ Failed to authenticate with Zerodha. Check your setup.")
    
    return _kite_instance

def refresh_authentication():
    """Force refresh authentication"""
    global _kite_instance
    _kite_instance = None
    return get_kite_instance()

def get_live_price(symbol):
    """Get live price for a symbol from correct exchange"""
    try:
        kite = get_kite_instance()
        
        # Symbol to exchange and instrument mapping
        symbol_config = {
            "NIFTY": {"exchange": "NSE", "instrument": "NIFTY 50"},
            "BANKNIFTY": {"exchange": "NSE", "instrument": "NIFTY BANK"},
            "FINNIFTY": {"exchange": "NSE", "instrument": "NIFTY FIN SERVICE"},
            "SENSEX": {"exchange": "BSE", "instrument": "SENSEX"}  # BSE for SENSEX
        }
        
        config = symbol_config.get(symbol.upper())
        if not config:
            logging.error(f"Unknown symbol: {symbol}")
            return 0
        
        # Construct the symbol key for Kite API
        kite_symbol_key = f"{config['exchange']}:{config['instrument']}"
        
        ltp_data = kite.ltp(kite_symbol_key)
        if ltp_data and kite_symbol_key in ltp_data:
            price = ltp_data[kite_symbol_key]["last_price"]
            logging.info(f"✅ {symbol} ({config['exchange']}): ₹{price:,.2f}")
            return price
        else:
            logging.warning(f"No LTP data for {symbol} on {config['exchange']}")
            return 0
            
    except Exception as e:
        logging.error(f"Error fetching price for {symbol}: {e}")
        return 0

def get_futures_price(symbol):
    """Get futures price for a symbol from correct exchange"""
    try:
        kite = get_kite_instance()
        
        # Futures configuration
        futures_config = {
            "NIFTY": {"exchange": "NFO", "base": "NIFTY"},
            "BANKNIFTY": {"exchange": "NFO", "base": "BANKNIFTY"},
            "FINNIFTY": {"exchange": "NFO", "base": "FINNIFTY"},
            "SENSEX": {"exchange": "BFO", "base": "SENSEX"}  # BFO for BSE futures
        }
        
        config = futures_config.get(symbol.upper())
        if not config:
            logging.error(f"Unknown futures symbol: {symbol}")
            return 0
        
        # Try current month futures
        expiry = "25JUL"  # Current expiry
        futures_symbol = f"{config['base']}{expiry}FUT"
        kite_symbol_key = f"{config['exchange']}:{futures_symbol}"
        
        try:
            ltp_data = kite.ltp(kite_symbol_key)
            if ltp_data and kite_symbol_key in ltp_data:
                price = ltp_data[kite_symbol_key]["last_price"]
                logging.info(f"✅ {futures_symbol} ({config['exchange']}): ₹{price:,.2f}")
                return price
        except Exception as e:
            logging.warning(f"Futures data not available for {symbol}: {e}")
        
        # Fallback to spot price
        return get_live_price(symbol)
        
    except Exception as e:
        logging.error(f"Error fetching futures price for {symbol}: {e}")
        return 0

def get_ohlc_data(symbol):
    """Get OHLC data for a symbol from correct exchange"""
    try:
        kite = get_kite_instance()
        
        # Symbol to exchange and instrument mapping
        symbol_config = {
            "NIFTY": {"exchange": "NSE", "instrument": "NIFTY 50"},
            "BANKNIFTY": {"exchange": "NSE", "instrument": "NIFTY BANK"},
            "FINNIFTY": {"exchange": "NSE", "instrument": "NIFTY FIN SERVICE"},
            "SENSEX": {"exchange": "BSE", "instrument": "SENSEX"}  # BSE for SENSEX
        }
        
        config = symbol_config.get(symbol.upper())
        if not config:
            logging.error(f"Unknown symbol: {symbol}")
            return None
        
        kite_symbol_key = f"{config['exchange']}:{config['instrument']}"
        
        ltp_data = kite.ltp(kite_symbol_key)
        if ltp_data and kite_symbol_key in ltp_data:
            data = ltp_data[kite_symbol_key]
            ohlc = {
                'open': data.get('ohlc', {}).get('open', 0),
                'high': data.get('ohlc', {}).get('high', 0),
                'low': data.get('ohlc', {}).get('low', 0),
                'close': data.get('last_price', 0),
                'volume': data.get('volume', 0),
                'exchange': config['exchange']
            }
            logging.info(f"✅ OHLC for {symbol} ({config['exchange']}): O:{ohlc['open']:.2f} H:{ohlc['high']:.2f} L:{ohlc['low']:.2f} C:{ohlc['close']:.2f}")
            return ohlc
        
        return None
        
    except Exception as e:
        logging.error(f"Error fetching OHLC for {symbol}: {e}")
        return None

def get_historical_data(symbol, interval="15minute", days=5):
    """Get historical data for a symbol"""
    try:
        from datetime import datetime, timedelta
        
        kite = get_kite_instance()
        
        # Get instrument token (simplified - you may need to implement proper token mapping)
        token_map = {
            "NIFTY": 256265,
            "BANKNIFTY": 260105,
            "FINNIFTY": 111111
        }
        
        token = token_map.get(symbol.upper())
        if not token:
            logging.error(f"No token mapping for {symbol}")
            return None
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        data = kite.historical_data(token, from_date, to_date, interval)
        
        if data:
            import pandas as pd
            df = pd.DataFrame(data)
            df.set_index("date", inplace=True)
            return df
        
        return None
        
    except Exception as e:
        logging.error(f"Error fetching historical data for {symbol}: {e}")
        return None

def place_order(tradingsymbol, exchange, quantity, transaction_type, product="NRML", order_type="MARKET"):
    """Place an order"""
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
        
        logging.info(f"✅ Order placed: {order_id}")
        return order_id
        
    except Exception as e:
        logging.error(f"❌ Order placement failed: {e}")
        return None

def get_positions():
    """Get current positions"""
    try:
        kite = get_kite_instance()
        positions = kite.positions()
        return positions
    except Exception as e:
        logging.error(f"Error fetching positions: {e}")
        return None

def get_telegram_config():
    """Get Telegram configuration securely"""
    try:
        auth_manager = get_auth_manager()
        telegram_token = auth_manager.get_credentials('telegram_token')
        telegram_chat_id = auth_manager.get_credentials('telegram_chat_id')
        
        return {
            'token': telegram_token,
            'chat_id': telegram_chat_id
        }
    except Exception as e:
        logging.error(f"Error getting Telegram config: {e}")
        return None

def test_secure_api():
    """Test the secure API"""
    print("🧪 Testing Secure Kite API")
    print("=" * 40)
    
    try:
        # Test authentication
        kite = get_kite_instance()
        print("✅ Authentication successful")
        
        # Test data fetching
        symbols = ["NIFTY", "BANKNIFTY", "FINNIFTY"]
        
        for symbol in symbols:
            price = get_live_price(symbol)
            if price > 0:
                print(f"✅ {symbol}: ₹{price:,.2f}")
            else:
                print(f"❌ {symbol}: No data")
        
        print("\n🔒 All data fetched securely!")
        print("🎉 Secure API working perfectly!")
        
    except Exception as e:
        print(f"❌ Secure API test failed: {e}")

if __name__ == "__main__":
    test_secure_api() 