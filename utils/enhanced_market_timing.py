#!/usr/bin/env python3
"""
Enhanced Market Timing for NSE and BSE

This module handles market timing for both NSE and BSE exchanges
with proper timezone and trading hours management.
"""

import pytz
from datetime import datetime, time, date, timedelta
import logging

class EnhancedMarketTiming:
    """
    Enhanced market timing for NSE and BSE markets
    """
    
    def __init__(self):
        self.timezone = pytz.timezone("Asia/Kolkata")
        self.logger = logging.getLogger("EnhancedMarketTiming")
        
        # NSE Market Hours (IST) - NIFTY, BANKNIFTY, FINNIFTY
        self.nse_hours = {
            'pre_market_start': time(9, 0),    # 9:00 AM
            'market_open': time(9, 15),        # 9:15 AM
            'market_close': time(15, 30),      # 3:30 PM
            'post_market_end': time(15, 45)    # 3:45 PM
        }
        
        # BSE Market Hours (IST) - SENSEX
        self.bse_hours = {
            'pre_market_start': time(9, 0),    # 9:00 AM
            'market_open': time(9, 15),        # 9:15 AM
            'market_close': time(15, 30),      # 3:30 PM
            'post_market_end': time(15, 45)    # 3:45 PM
        }
        
        # Symbol to exchange mapping
        self.symbol_exchange_map = {
            'NIFTY': 'NSE',
            'BANKNIFTY': 'NSE', 
            'FINNIFTY': 'NSE',
            'SENSEX': 'BSE'  # SENSEX trades on BSE
        }
        
        # Market holidays (sample - update with actual NSE/BSE calendar)
        self.holidays_2025 = [
            date(2025, 1, 26),  # Republic Day
            date(2025, 3, 14),  # Holi
            date(2025, 4, 14),  # Ram Navami
            date(2025, 8, 15),  # Independence Day
            date(2025, 10, 2),  # Gandhi Jayanti
            date(2025, 11, 1),  # Diwali
            # Add more holidays as needed
        ]
    
    def get_current_time(self):
        """Get current time in Indian timezone"""
        return datetime.now(self.timezone)
    
    def get_exchange_for_symbol(self, symbol):
        """Get exchange for a given symbol"""
        return self.symbol_exchange_map.get(symbol.upper(), 'NSE')
    
    def get_market_hours(self, symbol):
        """Get market hours for a symbol based on its exchange"""
        exchange = self.get_exchange_for_symbol(symbol)
        
        if exchange == 'BSE':
            return self.bse_hours
        else:
            return self.nse_hours
    
    def is_weekday(self):
        """Check if current day is a weekday (Monday-Friday)"""
        current_time = self.get_current_time()
        return current_time.weekday() < 5  # 0=Monday, 4=Friday
    
    def is_holiday(self, check_date=None):
        """Check if given date (or today) is a market holiday"""
        if check_date is None:
            check_date = self.get_current_time().date()
        
        return check_date in self.holidays_2025
    
    def is_market_open(self, symbol='NIFTY'):
        """Check if market is open for a specific symbol"""
        if not self.is_weekday():
            self.logger.info("Market closed - Weekend")
            return False
        
        if self.is_holiday():
            self.logger.info("Market closed - Holiday")
            return False
        
        current_time = self.get_current_time()
        current_time_only = current_time.time()
        
        market_hours = self.get_market_hours(symbol)
        exchange = self.get_exchange_for_symbol(symbol)
        
        is_open = (market_hours['market_open'] <= current_time_only <= market_hours['market_close'])
        
        if is_open:
            self.logger.info(f"{exchange} market open for {symbol}")
        else:
            self.logger.info(f"{exchange} market closed for {symbol}")
        
        return is_open
    
    def is_pre_market(self, symbol='NIFTY'):
        """Check if in pre-market session"""
        if not self.is_weekday() or self.is_holiday():
            return False
        
        current_time = self.get_current_time().time()
        market_hours = self.get_market_hours(symbol)
        
        return (market_hours['pre_market_start'] <= current_time < market_hours['market_open'])
    
    def is_post_market(self, symbol='NIFTY'):
        """Check if in post-market session"""
        if not self.is_weekday() or self.is_holiday():
            return False
        
        current_time = self.get_current_time().time()
        market_hours = self.get_market_hours(symbol)
        
        return (market_hours['market_close'] < current_time <= market_hours['post_market_end'])
    
    def get_market_status(self, symbol='NIFTY'):
        """Get detailed market status for a symbol"""
        exchange = self.get_exchange_for_symbol(symbol)
        current_time = self.get_current_time()
        
        status = {
            'symbol': symbol,
            'exchange': exchange,
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S IST'),
            'is_weekday': self.is_weekday(),
            'is_holiday': self.is_holiday(),
            'is_market_open': self.is_market_open(symbol),
            'is_pre_market': self.is_pre_market(symbol),
            'is_post_market': self.is_post_market(symbol),
            'market_hours': self.get_market_hours(symbol)
        }
        
        # Determine overall status
        if not status['is_weekday']:
            status['status'] = 'WEEKEND'
        elif status['is_holiday']:
            status['status'] = 'HOLIDAY'
        elif status['is_pre_market']:
            status['status'] = 'PRE_MARKET'
        elif status['is_market_open']:
            status['status'] = 'MARKET_OPEN'
        elif status['is_post_market']:
            status['status'] = 'POST_MARKET'
        else:
            status['status'] = 'MARKET_CLOSED'
        
        return status
    
    def get_next_market_open(self, symbol='NIFTY'):
        """Get next market open time for a symbol"""
        current_time = self.get_current_time()
        market_hours = self.get_market_hours(symbol)
        
        # If market is open today and we're before close
        if self.is_weekday() and not self.is_holiday():
            today_open = current_time.replace(
                hour=market_hours['market_open'].hour,
                minute=market_hours['market_open'].minute,
                second=0,
                microsecond=0
            )
            
            if current_time < today_open:
                return today_open
        
        # Find next weekday
        next_day = current_time + timedelta(days=1)
        while next_day.weekday() >= 5 or self.is_holiday(next_day.date()):
            next_day += timedelta(days=1)
        
        next_open = next_day.replace(
            hour=market_hours['market_open'].hour,
            minute=market_hours['market_open'].minute,
            second=0,
            microsecond=0
        )
        
        return next_open
    
    def should_trade_now(self, symbol='NIFTY'):
        """Check if trading should be active for a symbol"""
        market_status = self.get_market_status(symbol)
        
        # Trade only during market hours
        trading_allowed = market_status['status'] == 'MARKET_OPEN'
        
        if trading_allowed:
            self.logger.info(f"✅ Trading allowed for {symbol} on {market_status['exchange']}")
        else:
            self.logger.info(f"❌ Trading not allowed for {symbol} - Status: {market_status['status']}")
        
        return trading_allowed
    
    def get_all_markets_status(self):
        """Get status for all symbols"""
        symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'SENSEX']
        all_status = {}
        
        for symbol in symbols:
            all_status[symbol] = self.get_market_status(symbol)
        
        return all_status

def test_market_timing():
    """Test the enhanced market timing system"""
    print("🕐 ENHANCED MARKET TIMING TEST")
    print("=" * 60)
    
    timing = EnhancedMarketTiming()
    current_time = timing.get_current_time()
    
    print(f"⏰ Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"📅 Weekday: {timing.is_weekday()}")
    print(f"🏖️ Holiday: {timing.is_holiday()}")
    print()
    
    # Test all symbols
    symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'SENSEX']
    
    for symbol in symbols:
        status = timing.get_market_status(symbol)
        exchange = status['exchange']
        market_status = status['status']
        
        print(f"📊 {symbol} ({exchange}):")
        print(f"   Status: {market_status}")
        print(f"   Market Open: {status['is_market_open']}")
        print(f"   Trading Allowed: {timing.should_trade_now(symbol)}")
        
        if exchange == 'BSE':
            print(f"   ✅ BSE market timing configured for SENSEX")
        
        print()
    
    # Show next market open times
    print("🔜 NEXT MARKET OPEN TIMES:")
    print("-" * 30)
    for symbol in symbols:
        next_open = timing.get_next_market_open(symbol)
        exchange = timing.get_exchange_for_symbol(symbol)
        print(f"{symbol} ({exchange}): {next_open.strftime('%Y-%m-%d %H:%M:%S IST')}")

    def is_friday_315(self) -> bool:
        """Check if it's Friday 3:15 PM (early close time)"""
        now = self.get_current_time()
        return (now.weekday() == 4 and  # Friday
                now.hour == 15 and 
                now.minute >= 15)
    
    def is_within_first_15_minutes(self) -> bool:
        """Check if we're within first 15 minutes of market open"""
        now = self.get_current_time()
        current_time = now.time()
        
        # Market opens at 9:15 AM, so first 15 minutes is 9:15-9:30
        first_15_start = time(9, 15)
        first_15_end = time(9, 30)
        
        return (self.is_market_open() and 
                first_15_start <= current_time <= first_15_end)

# Global convenience functions for backward compatibility
def is_market_open(symbol='NIFTY') -> bool:
    """Global function for backward compatibility"""
    timing = EnhancedMarketTiming()
    return timing.is_market_open(symbol)

def get_market_status(symbol='NIFTY') -> dict:
    """Global function for backward compatibility"""
    timing = EnhancedMarketTiming()
    return timing.get_market_status(symbol)

def is_friday_315() -> bool:
    """Global function for backward compatibility"""
    timing = EnhancedMarketTiming()
    return timing.is_friday_315()

def is_within_first_15_minutes() -> bool:
    """Global function for backward compatibility"""
    timing = EnhancedMarketTiming()
    return timing.is_within_first_15_minutes()

if __name__ == "__main__":
    test_market_timing() 