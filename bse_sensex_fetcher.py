#!/usr/bin/env python3
"""
🏛️ BSE SENSEX Data Fetcher for Saki
Fetches real-time BSE SENSEX data since SENSEX is on BSE, not NSE
"""

import requests
import json
import logging
from datetime import datetime
import pytz

INDIAN_TZ = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current Indian time"""
    return datetime.now(INDIAN_TZ)

class BSESensexFetcher:
    """
    🏛️ BSE SENSEX Data Fetcher
    Since SENSEX is on BSE (Bombay Stock Exchange), not NSE
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # BSE API endpoints (fallback sources)
        self.bse_endpoints = [
            "https://api.bseindia.com/BseIndiaAPI/api/SensexData/w",
            "https://www.bseindia.com/sensex/sens_live_data.aspx",
        ]
        
        # Yahoo Finance for SENSEX (BSE:SENSEX)
        self.yahoo_sensex = "https://query1.finance.yahoo.com/v8/finance/chart/^BSESN"
        
        # Alternative APIs
        self.alternative_apis = [
            "https://api.worldtradingdata.com/api/v1/stock?symbol=BSE:SENSEX",
            "https://api.twelvedata.com/quote?symbol=BSE:SENSEX",
        ]
        
        # Fallback SENSEX price
        self.fallback_sensex = 81867.55
        
    def get_sensex_price(self):
        """
        Get real-time BSE SENSEX price with multiple fallbacks
        """
        current_time = get_indian_time().strftime('%H:%M:%S IST')
        
        # Method 1: Try Yahoo Finance for BSE SENSEX
        try:
            self.logger.info(f"🏛️ Fetching BSE SENSEX from Yahoo Finance at {current_time}")
            
            response = requests.get(self.yahoo_sensex, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        sensex_price = result['meta']['regularMarketPrice']
                        
                        self.logger.info(f"✅ BSE SENSEX fetched: ₹{sensex_price:,.2f}")
                        return {
                            'price': sensex_price,
                            'source': 'Yahoo Finance BSE',
                            'timestamp': current_time,
                            'status': 'SUCCESS'
                        }
        except Exception as e:
            self.logger.warning(f"⚠️ Yahoo Finance BSE SENSEX failed: {e}")
        
        # Method 2: Try NSE India (sometimes has BSE data)
        try:
            self.logger.info(f"🏛️ Trying NSE India for SENSEX reference at {current_time}")
            
            # NSE sometimes provides BSE references
            nse_url = "https://www.nseindia.com/api/allIndices"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.nseindia.com/'
            }
            
            response = requests.get(nse_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Look for BSE SENSEX reference
                for item in data.get('data', []):
                    if item.get('index', '').upper() in ['BSE SENSEX', 'SENSEX']:
                        sensex_price = float(item.get('last', 0))
                        if sensex_price > 0:
                            self.logger.info(f"✅ BSE SENSEX from NSE reference: ₹{sensex_price:,.2f}")
                            return {
                                'price': sensex_price,
                                'source': 'NSE BSE Reference',
                                'timestamp': current_time,
                                'status': 'SUCCESS'
                            }
        except Exception as e:
            self.logger.warning(f"⚠️ NSE BSE reference failed: {e}")
        
        # Method 3: Try financial data APIs
        try:
            self.logger.info(f"🏛️ Trying financial APIs for BSE SENSEX at {current_time}")
            
            # Generic financial API endpoints
            financial_apis = [
                "https://api.polygon.io/v2/last/trade/BSE:SENSEX",
                "https://financialmodelingprep.com/api/v3/quote/BSE:SENSEX",
            ]
            
            for api_url in financial_apis:
                try:
                    response = requests.get(api_url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Try to extract price from different response formats
                        price = None
                        if isinstance(data, list) and len(data) > 0:
                            item = data[0]
                            price = item.get('price') or item.get('last') or item.get('close')
                        elif isinstance(data, dict):
                            price = data.get('price') or data.get('last') or data.get('close')
                        
                        if price and float(price) > 0:
                            sensex_price = float(price)
                            self.logger.info(f"✅ BSE SENSEX from financial API: ₹{sensex_price:,.2f}")
                            return {
                                'price': sensex_price,
                                'source': 'Financial API',
                                'timestamp': current_time, 
                                'status': 'SUCCESS'
                            }
                except:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Financial APIs failed: {e}")
        
        # Method 4: Web scraping BSE website (last resort)
        try:
            self.logger.info(f"🏛️ Attempting BSE website scraping at {current_time}")
            
            bse_url = "https://www.bseindia.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(bse_url, headers=headers, timeout=15)
            if response.status_code == 200:
                content = response.text
                
                # Look for SENSEX price in HTML content
                import re
                
                # Common patterns for SENSEX price
                patterns = [
                    r'sensex["\s:]*(\d+\.?\d*)',
                    r'SENSEX["\s:]*(\d+\.?\d*)',
                    r'"price":\s*"?(\d+\.?\d*)"?.*sensex',
                    r'data-value="(\d+\.?\d*)".*sensex'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        try:
                            price = float(match)
                            if 70000 <= price <= 100000:  # Reasonable SENSEX range
                                self.logger.info(f"✅ BSE SENSEX scraped: ₹{price:,.2f}")
                                return {
                                    'price': price,
                                    'source': 'BSE Website Scrape',
                                    'timestamp': current_time,
                                    'status': 'SUCCESS'
                                }
                        except:
                            continue
                            
        except Exception as e:
            self.logger.warning(f"⚠️ BSE website scraping failed: {e}")
        
        # Fallback: Use stored fallback price
        self.logger.warning(f"⚠️ All BSE SENSEX sources failed, using fallback: ₹{self.fallback_sensex:,.2f}")
        return {
            'price': self.fallback_sensex,
            'source': 'Fallback Price',
            'timestamp': current_time,
            'status': 'FALLBACK'
        }
    
    def get_bse_market_status(self):
        """Get BSE market status"""
        current_time = get_indian_time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # BSE market hours: 9:15 AM to 3:30 PM IST (same as NSE)
        market_open = (current_hour > 9) or (current_hour == 9 and current_minute >= 15)
        market_close = (current_hour >= 15 and current_minute >= 30)
        
        if market_open and not market_close:
            return "OPEN"
        else:
            return "CLOSED"
    
    def update_fallback_sensex(self, price):
        """Update fallback SENSEX price"""
        if price and 70000 <= price <= 100000:  # Reasonable range
            self.fallback_sensex = price
            self.logger.info(f"📊 Fallback BSE SENSEX updated to ₹{price:,.2f}")

# Global BSE fetcher instance
bse_fetcher = None

def get_bse_fetcher():
    """Get BSE SENSEX fetcher instance"""
    global bse_fetcher
    if bse_fetcher is None:
        bse_fetcher = BSESensexFetcher()
    return bse_fetcher

def get_sensex_price():
    """Get BSE SENSEX price (easy function)"""
    fetcher = get_bse_fetcher()
    result = fetcher.get_sensex_price()
    return result['price']

def get_sensex_data():
    """Get complete BSE SENSEX data"""
    fetcher = get_bse_fetcher()
    return fetcher.get_sensex_price()

if __name__ == "__main__":
    # Test BSE SENSEX fetching
    fetcher = BSESensexFetcher()
    
    print("🏛️ Testing BSE SENSEX Data Fetcher")
    print("=" * 50)
    
    result = fetcher.get_sensex_price()
    
    print(f"💰 BSE SENSEX: ₹{result['price']:,.2f}")
    print(f"📊 Source: {result['source']}")
    print(f"⏰ Time: {result['timestamp']}")
    print(f"✅ Status: {result['status']}")
    
    print("\n🏛️ BSE SENSEX data ready for Saki!")
