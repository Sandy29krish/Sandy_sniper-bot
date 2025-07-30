import requests
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

class NSEOptionChain:
    """
    NSE Option Chain integration for real-time option data
    Fetches premiums, Greeks, OI data directly from NSE
    """
    
    def __init__(self):
        self.base_url = "https://www.nseindia.com/api/option-chain-indices"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Cache for option data (5 minute cache)
        self.option_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Symbol mapping for NSE API
        self.symbol_mapping = {
            'NIFTY': 'NIFTY',
            'BANKNIFTY': 'BANKNIFTY', 
            'SENSEX': 'SENSEX',
            'FINNIFTY': 'FINNIFTY'
        }
    
    def get_option_chain(self, symbol: str) -> Optional[Dict]:
        """
        Get complete option chain data from NSE
        Returns: Dictionary with CE/PE data, premiums, OI, Greeks
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_option_chain"
            if self._is_cache_valid(cache_key):
                logger.info(f"📊 Using cached option chain for {symbol}")
                return self.option_cache[cache_key]['data']
            
            # Map symbol to NSE format
            nse_symbol = self.symbol_mapping.get(symbol, symbol)
            
            # Fetch from NSE
            url = f"{self.base_url}?symbol={nse_symbol}"
            logger.info(f"🔍 Fetching option chain for {symbol} from NSE...")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process and structure the data
                processed_data = self._process_option_chain_data(data, symbol)
                
                # Cache the result
                self.option_cache[cache_key] = {
                    'data': processed_data,
                    'timestamp': datetime.now()
                }
                
                logger.info(f"✅ Successfully fetched option chain for {symbol}")
                return processed_data
            else:
                logger.error(f"❌ NSE API error for {symbol}: Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching option chain for {symbol}: {e}")
            return None
    
    def get_option_premium(self, symbol: str, strike: int, option_type: str, expiry: str) -> Optional[float]:
        """
        Get specific option premium
        Args:
            symbol: NIFTY, BANKNIFTY, etc.
            strike: Strike price
            option_type: 'CE' or 'PE'
            expiry: Expiry date in 'DDMMMYYYY' format
        Returns: Premium price or None
        """
        try:
            option_chain = self.get_option_chain(symbol)
            if not option_chain:
                return None
            
            # Find the specific option
            records = option_chain.get('records', {}).get('data', [])
            
            for record in records:
                if record.get('strikePrice') == strike:
                    option_data = record.get(option_type, {})
                    if option_data and option_data.get('expiryDate') == expiry:
                        premium = option_data.get('lastPrice', 0)
                        logger.info(f"💰 {symbol} {strike}{option_type} premium: ₹{premium}")
                        return premium
            
            logger.warning(f"⚠️ Option not found: {symbol} {strike}{option_type} {expiry}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting option premium: {e}")
            return None
    
    def get_monthly_expiry_dates(self, symbol: str) -> List[str]:
        """
        Get list of monthly expiry dates for the symbol
        Returns: List of expiry dates in 'DDMMMYYYY' format
        """
        try:
            option_chain = self.get_option_chain(symbol)
            if not option_chain:
                return []
            
            # Extract expiry dates
            expiry_dates = option_chain.get('records', {}).get('expiryDates', [])
            
            # Filter for monthly expiries (typically last Thursday of month)
            monthly_expiries = self._filter_monthly_expiries(expiry_dates)
            
            logger.info(f"📅 Monthly expiries for {symbol}: {monthly_expiries}")
            return monthly_expiries
            
        except Exception as e:
            logger.error(f"❌ Error getting expiry dates for {symbol}: {e}")
            return []
    
    def get_current_expiry(self, symbol: str) -> Optional[str]:
        """Get current month expiry date"""
        try:
            monthly_expiries = self.get_monthly_expiry_dates(symbol)
            if not monthly_expiries:
                return None
            
            # Return the nearest expiry
            current_expiry = monthly_expiries[0]
            logger.info(f"📅 Current expiry for {symbol}: {current_expiry}")
            return current_expiry
            
        except Exception as e:
            logger.error(f"❌ Error getting current expiry for {symbol}: {e}")
            return None
    
    def get_next_expiry(self, symbol: str) -> Optional[str]:
        """Get next month expiry date"""
        try:
            monthly_expiries = self.get_monthly_expiry_dates(symbol)
            if len(monthly_expiries) < 2:
                return None
            
            # Return the second expiry (next month)
            next_expiry = monthly_expiries[1]
            logger.info(f"📅 Next expiry for {symbol}: {next_expiry}")
            return next_expiry
            
        except Exception as e:
            logger.error(f"❌ Error getting next expiry for {symbol}: {e}")
            return None
    
    def get_option_greeks(self, symbol: str, strike: int, option_type: str, expiry: str) -> Optional[Dict]:
        """
        Get option Greeks (Delta, Gamma, Theta, Vega)
        Returns: Dictionary with Greeks data
        """
        try:
            option_chain = self.get_option_chain(symbol)
            if not option_chain:
                return None
            
            records = option_chain.get('records', {}).get('data', [])
            
            for record in records:
                if record.get('strikePrice') == strike:
                    option_data = record.get(option_type, {})
                    if option_data and option_data.get('expiryDate') == expiry:
                        greeks = {
                            'delta': option_data.get('delta', 0),
                            'gamma': option_data.get('gamma', 0),
                            'theta': option_data.get('theta', 0),
                            'vega': option_data.get('vega', 0),
                            'iv': option_data.get('impliedVolatility', 0)
                        }
                        logger.info(f"📊 Greeks for {symbol} {strike}{option_type}: {greeks}")
                        return greeks
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting option Greeks: {e}")
            return None
    
    def get_option_oi_data(self, symbol: str, strike: int, option_type: str, expiry: str) -> Optional[Dict]:
        """
        Get Open Interest and volume data
        Returns: Dictionary with OI and volume data
        """
        try:
            option_chain = self.get_option_chain(symbol)
            if not option_chain:
                return None
            
            records = option_chain.get('records', {}).get('data', [])
            
            for record in records:
                if record.get('strikePrice') == strike:
                    option_data = record.get(option_type, {})
                    if option_data and option_data.get('expiryDate') == expiry:
                        oi_data = {
                            'openInterest': option_data.get('openInterest', 0),
                            'changeinOpenInterest': option_data.get('changeinOpenInterest', 0),
                            'totalTradedVolume': option_data.get('totalTradedVolume', 0),
                            'totalBuyQuantity': option_data.get('totalBuyQuantity', 0),
                            'totalSellQuantity': option_data.get('totalSellQuantity', 0),
                            'bidQty': option_data.get('bidQty', 0),
                            'askQty': option_data.get('askQty', 0),
                            'bidprice': option_data.get('bidprice', 0),
                            'askPrice': option_data.get('askPrice', 0)
                        }
                        logger.info(f"📈 OI data for {symbol} {strike}{option_type}: OI={oi_data['openInterest']}")
                        return oi_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting option OI data: {e}")
            return None
    
    def _process_option_chain_data(self, raw_data: Dict, symbol: str) -> Dict:
        """Process raw NSE option chain data"""
        try:
            processed = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'underlyingValue': raw_data.get('records', {}).get('underlyingValue', 0),
                'records': raw_data.get('records', {}),
                'expiry_dates': raw_data.get('records', {}).get('expiryDates', []),
                'strike_prices': []
            }
            
            # Extract unique strike prices
            records = raw_data.get('records', {}).get('data', [])
            strike_prices = list(set(record.get('strikePrice', 0) for record in records))
            processed['strike_prices'] = sorted(strike_prices)
            
            return processed
            
        except Exception as e:
            logger.error(f"❌ Error processing option chain data: {e}")
            return {}
    
    def _filter_monthly_expiries(self, expiry_dates: List[str]) -> List[str]:
        """Filter for monthly expiries (last Thursday of each month)"""
        try:
            monthly_expiries = []
            
            for expiry_str in expiry_dates:
                try:
                    # Parse expiry date
                    expiry_date = datetime.strptime(expiry_str, '%d-%b-%Y')
                    
                    # Check if it's last Thursday of the month
                    if self._is_last_thursday(expiry_date):
                        monthly_expiries.append(expiry_str)
                        
                except ValueError:
                    continue
            
            return sorted(monthly_expiries)[:3]  # Return next 3 monthly expiries
            
        except Exception as e:
            logger.error(f"❌ Error filtering monthly expiries: {e}")
            return expiry_dates[:3]  # Fallback to first 3 expiries
    
    def _is_last_thursday(self, date: datetime) -> bool:
        """Check if date is last Thursday of the month"""
        try:
            # Check if it's Thursday (weekday 3)
            if date.weekday() != 3:
                return False
            
            # Check if it's the last Thursday
            # Add 7 days and see if we're still in the same month
            next_thursday = date + timedelta(days=7)
            return next_thursday.month != date.month
            
        except Exception:
            return False
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.option_cache:
            return False
        
        cache_time = self.option_cache[cache_key]['timestamp']
        time_diff = (datetime.now() - cache_time).total_seconds()
        
        return time_diff < self.cache_duration

# Global instance
nse_option_chain = NSEOptionChain()

# Convenience functions
def get_option_premium(symbol: str, strike: int, option_type: str, expiry: str) -> Optional[float]:
    """Get option premium from NSE"""
    return nse_option_chain.get_option_premium(symbol, strike, option_type, expiry)

def get_current_expiry(symbol: str) -> Optional[str]:
    """Get current month expiry"""
    return nse_option_chain.get_current_expiry(symbol)

def get_next_expiry(symbol: str) -> Optional[str]:
    """Get next month expiry"""
    return nse_option_chain.get_next_expiry(symbol)

def get_option_oi_data(symbol: str, strike: int, option_type: str, expiry: str) -> Optional[Dict]:
    """Get option OI and volume data"""
    return nse_option_chain.get_option_oi_data(symbol, strike, option_type, expiry) 