"""
Market Timing Utilities
Handles market open/close times, trading sessions, and market status
"""

import os
import pytz
from datetime import datetime, time
import requests
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Indian Market timezone
IST = pytz.timezone('Asia/Kolkata')

# Market hours configuration
MARKET_CONFIG = {
    'pre_market_start': time(9, 0),    # 9:00 AM
    'market_open': time(9, 15),        # 9:15 AM  
    'market_close': time(15, 30),      # 3:30 PM
    'post_market_end': time(15, 45),   # 3:45 PM
    'friday_early_close': time(15, 15) # 3:15 PM Friday
}

# Trading session definitions
TRADING_SESSIONS = {
    'morning': (time(9, 15), time(11, 30)),
    'afternoon': (time(11, 30), time(15, 30)),
    'pre_market': (time(9, 0), time(9, 15)),
    'post_market': (time(15, 30), time(15, 45))
}

def get_current_ist_time() -> datetime:
    """Get current time in IST"""
    return datetime.now(IST)

def is_market_open() -> bool:
    """
    Check if Indian stock market is currently open
    Returns True if market is open for trading
    """
    try:
        now = get_current_ist_time()
        current_time = now.time()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Market closed on weekends
        if weekday >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check if it's a holiday (simplified check)
        if is_market_holiday(now.date()):
            return False
        
        # Friday early close at 3:15 PM
        if weekday == 4:  # Friday
            return MARKET_CONFIG['market_open'] <= current_time <= MARKET_CONFIG['friday_early_close']
        
        # Regular trading hours (Monday-Thursday)
        return MARKET_CONFIG['market_open'] <= current_time <= MARKET_CONFIG['market_close']
        
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return False

def is_trading_time() -> bool:
    """
    Check if it's currently trading time (includes pre-market and market hours)
    Returns True during 8:00 AM - 4:00 PM on trading days
    """
    try:
        now = get_current_ist_time()
        current_time = now.time()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Market closed on weekends
        if weekday >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check if it's a holiday
        if is_market_holiday(now.date()):
            return False
        
        # Trading time: 8:00 AM to 4:00 PM (includes pre-market and post-market)
        trading_start = time(8, 0)   # 8:00 AM
        trading_end = time(16, 0)    # 4:00 PM
        
        # Friday early end at 3:15 PM
        if weekday == 4:  # Friday
            trading_end = time(15, 15)  # 3:15 PM
        
        return trading_start <= current_time <= trading_end
        
    except Exception as e:
        logger.error(f"Error checking trading time: {e}")
        return False

def get_market_status() -> Dict[str, str]:
    """
    Get detailed market status information
    Returns dict with status and descriptive message
    """
    try:
        now = get_current_ist_time()
        current_time = now.time()
        weekday = now.weekday()
        
        # Weekend check
        if weekday >= 5:
            next_monday = now.replace(hour=9, minute=15, second=0, microsecond=0)
            days_until_monday = 7 - weekday
            if days_until_monday == 7:
                days_until_monday = 0
            next_monday = next_monday.replace(day=now.day + days_until_monday)
            
            return {
                'status': 'CLOSED_WEEKEND',
                'message': f'Market closed for weekend. Opens Monday at 9:15 AM',
                'next_open': next_monday.isoformat()
            }
        
        # Holiday check
        if is_market_holiday(now.date()):
            return {
                'status': 'CLOSED_HOLIDAY',
                'message': 'Market closed for holiday',
                'next_open': 'Check NSE holiday calendar'
            }
        
        # Pre-market
        if MARKET_CONFIG['pre_market_start'] <= current_time < MARKET_CONFIG['market_open']:
            return {
                'status': 'PRE_MARKET',
                'message': f'Pre-market session. Market opens at 9:15 AM',
                'time_to_open': str(MARKET_CONFIG['market_open'])
            }
        
        # Market open - Friday early close
        if weekday == 4:  # Friday
            if MARKET_CONFIG['market_open'] <= current_time <= MARKET_CONFIG['friday_early_close']:
                return {
                    'status': 'OPEN',
                    'message': f'Market open (Friday early close at 3:15 PM)',
                    'session': get_current_session(current_time)
                }
            elif current_time > MARKET_CONFIG['friday_early_close']:
                return {
                    'status': 'CLOSED',
                    'message': 'Market closed (Friday early close)',
                    'next_open': 'Monday 9:15 AM'
                }
        
        # Regular market hours
        if MARKET_CONFIG['market_open'] <= current_time <= MARKET_CONFIG['market_close']:
            return {
                'status': 'OPEN',
                'message': f'Market open - {get_current_session(current_time)} session',
                'session': get_current_session(current_time)
            }
        
        # Post-market
        if MARKET_CONFIG['market_close'] < current_time <= MARKET_CONFIG['post_market_end']:
            return {
                'status': 'POST_MARKET',
                'message': 'Post-market session',
                'next_open': 'Tomorrow 9:15 AM'
            }
        
        # After hours
        return {
            'status': 'CLOSED',
            'message': 'Market closed',
            'next_open': 'Tomorrow 9:15 AM' if weekday < 4 else 'Monday 9:15 AM'
        }
        
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        return {
            'status': 'ERROR',
            'message': f'Unable to determine market status: {e}',
            'next_open': 'Unknown'
        }

def get_current_session(current_time: time) -> str:
    """Get the current trading session name"""
    for session_name, (start_time, end_time) in TRADING_SESSIONS.items():
        if start_time <= current_time <= end_time:
            return session_name
    return 'unknown'

def is_friday_315() -> bool:
    """Check if it's Friday 3:15 PM or later (forced exit time)"""
    try:
        now = get_current_ist_time()
        return (now.weekday() == 4 and  # Friday
                now.time() >= MARKET_CONFIG['friday_early_close'])
    except Exception as e:
        logger.error(f"Error checking Friday 3:15: {e}")
        return False

def is_within_first_15_minutes() -> bool:
    """Check if we're within the first 15 minutes of market open"""
    try:
        now = get_current_ist_time()
        current_time = now.time()
        
        # Only check if market is actually open
        if not is_market_open():
            return False
        
        # Check if within first 15 minutes (9:15 - 9:30)
        market_open = MARKET_CONFIG['market_open']
        first_15_end = time(9, 30)
        
        return market_open <= current_time <= first_15_end
        
    except Exception as e:
        logger.error(f"Error checking first 15 minutes: {e}")
        return False

def is_market_holiday(date_to_check) -> bool:
    """
    Check if given date is a market holiday
    This is a simplified version - in production, you should fetch from NSE API
    """
    try:
        # Common holidays (simplified list)
        # In production, fetch from NSE holiday calendar API
        common_holidays = [
            # Add major holidays here
            # Format: (month, day)
            (1, 26),   # Republic Day
            (8, 15),   # Independence Day  
            (10, 2),   # Gandhi Jayanti
            # Add more holidays as needed
        ]
        
        month_day = (date_to_check.month, date_to_check.day)
        return month_day in common_holidays
        
    except Exception as e:
        logger.error(f"Error checking holiday: {e}")
        return False

def get_next_trading_day() -> datetime:
    """Get the next trading day"""
    try:
        now = get_current_ist_time()
        next_day = now
        
        # Keep incrementing until we find a trading day
        while True:
            next_day = next_day.replace(day=next_day.day + 1)
            
            # Skip weekends
            if next_day.weekday() >= 5:
                continue
                
            # Skip holidays  
            if is_market_holiday(next_day.date()):
                continue
                
            return next_day.replace(hour=9, minute=15, second=0, microsecond=0)
            
    except Exception as e:
        logger.error(f"Error getting next trading day: {e}")
        # Fallback to tomorrow
        return (get_current_ist_time() + datetime.timedelta(days=1)).replace(hour=9, minute=15)

def time_until_market_open() -> Optional[int]:
    """Get seconds until market opens. Returns None if market is open"""
    if is_market_open():
        return None
        
    try:
        next_open = get_next_trading_day()
        now = get_current_ist_time()
        time_diff = next_open - now
        return int(time_diff.total_seconds())
    except Exception as e:
        logger.error(f"Error calculating time until open: {e}")
        return None

def time_until_market_close() -> Optional[int]:
    """Get seconds until market closes. Returns None if market is closed"""
    if not is_market_open():
        return None
        
    try:
        now = get_current_ist_time()
        
        # Friday early close
        if now.weekday() == 4:
            close_time = now.replace(
                hour=MARKET_CONFIG['friday_early_close'].hour,
                minute=MARKET_CONFIG['friday_early_close'].minute,
                second=0, microsecond=0
            )
        else:
            close_time = now.replace(
                hour=MARKET_CONFIG['market_close'].hour,
                minute=MARKET_CONFIG['market_close'].minute,
                second=0, microsecond=0
            )
        
        time_diff = close_time - now
        return int(time_diff.total_seconds())
        
    except Exception as e:
        logger.error(f"Error calculating time until close: {e}")
        return None

def is_trading_session(session_name: str) -> bool:
    """Check if we're in a specific trading session"""
    try:
        now = get_current_ist_time()
        current_time = now.time()
        
        if session_name not in TRADING_SESSIONS:
            return False
            
        start_time, end_time = TRADING_SESSIONS[session_name]
        return start_time <= current_time <= end_time
        
    except Exception as e:
        logger.error(f"Error checking trading session {session_name}: {e}")
        return False

# Market timing summary for logging
def get_market_timing_summary() -> str:
    """Get a summary of current market timing status"""
    try:
        now = get_current_ist_time()
        status = get_market_status()
        
        summary = f"📅 {now.strftime('%Y-%m-%d %H:%M:%S IST')}\n"
        summary += f"📊 Market Status: {status['status']}\n"
        summary += f"💬 {status['message']}\n"
        
        if 'session' in status:
            summary += f"🕒 Current Session: {status['session']}\n"
            
        if not is_market_open():
            time_to_open = time_until_market_open()
            if time_to_open:
                hours = time_to_open // 3600
                minutes = (time_to_open % 3600) // 60
                summary += f"⏰ Time to open: {hours}h {minutes}m\n"
        else:
            time_to_close = time_until_market_close()
            if time_to_close:
                hours = time_to_close // 3600
                minutes = (time_to_close % 3600) // 60
                summary += f"⏰ Time to close: {hours}h {minutes}m\n"
        
        return summary
        
    except Exception as e:
        return f"❌ Error getting timing summary: {e}"

if __name__ == "__main__":
    # Test the market timing functions
    print("=== Market Timing Test ===")
    print(get_market_timing_summary())
    print(f"Market Open: {is_market_open()}")
    print(f"Friday 3:15: {is_friday_315()}")
    print(f"First 15 minutes: {is_within_first_15_minutes()}")
