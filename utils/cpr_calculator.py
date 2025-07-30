import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from utils.nse_data import get_live_ohlc

logger = logging.getLogger(__name__)

class DynamicCPRCalculator:
    """
    Dynamic Central Pivot Range (CPR) Calculator
    
    Calculates CPR levels based on different timeframes:
    - Daily CPR: Based on previous day's high, low, close
    - Weekly CPR: Based on previous week's high, low, close
    - Monthly CPR: Based on previous month's high, low, close
    - Intraday CPR: Based on current session's high, low, close
    """
    
    def __init__(self):
        self.cpr_cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def calculate_cpr_levels(self, high, low, close):
        """
        Calculate CPR levels using the exact method from user's data
        Based on user's data: Pivot=24989.30, BC=25060.55, TC=24918.05
        """
        try:
            # Standard CPR calculation
            pivot = (high + low + close) / 3
            
            # User's method appears to use different BC/TC calculation
            # From the data pattern, it seems BC > Pivot > TC
            bc = (high + low) / 2  # Bottom Central
            tc = (2 * pivot) - bc  # Top Central
            
            return {
                'pivot': round(pivot, 2),
                'cpr_top': round(tc, 2),      # Top Central (lower value)
                'cpr_bottom': round(bc, 2),   # Bottom Central (higher value)
                'cpr_width': round(abs(bc - tc), 2),
                'cpr_strength': 'narrow' if abs(bc - tc) < (pivot * 0.005) else 'wide'
            }
        except Exception as e:
            logger.error(f"Error calculating CPR levels: {e}")
            return None
    
    def get_intraday_cpr(self, symbol):
        """
        Calculate intraday CPR based on current session's live data
        """
        cache_key = f"{symbol}_intraday_{datetime.now().strftime('%Y-%m-%d-%H')}"
        
        # Check cache first
        if cache_key in self.cpr_cache:
            cache_time, cpr_data = self.cpr_cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_duration:
                return cpr_data
        
        try:
            # Get live OHLC data from Zerodha Kite
            ohlc_data = get_live_ohlc(symbol)
            if not ohlc_data:
                logger.warning(f"No live OHLC data available for {symbol}")
                return None
            
            # Calculate CPR from live data
            cpr_levels = self.calculate_cpr_levels(
                ohlc_data['high'],
                ohlc_data['low'], 
                ohlc_data['close']
            )
            
            if cpr_levels:
                self.cpr_cache[cache_key] = (datetime.now(), cpr_levels)
                logger.info(f"Intraday CPR for {symbol}: Pivot={cpr_levels['pivot']}, "
                          f"Top={cpr_levels['cpr_top']}, Bottom={cpr_levels['cpr_bottom']}")
            
            return cpr_levels
            
        except Exception as e:
            logger.error(f"Error calculating intraday CPR for {symbol}: {e}")
            return None
    
    def get_multi_timeframe_cpr(self, symbol, timeframes=['intraday']):
        """
        Get CPR levels for multiple timeframes using live data
        """
        multi_cpr = {}
        
        for timeframe in timeframes:
            if timeframe == 'intraday':
                cpr_data = self.get_intraday_cpr(symbol)
            else:
                logger.warning(f"Unknown timeframe: {timeframe}")
                continue
                
            if cpr_data:
                multi_cpr[timeframe] = cpr_data
        
        return multi_cpr
    
    def validate_cpr_conditions(self, current_price, cpr_levels, signal_type):
        """
        Validate CPR conditions for trade entry
        
        Args:
            current_price: Current market price
            cpr_levels: CPR levels dict
            signal_type: 'bullish' or 'bearish'
            
        Returns:
            bool: True if CPR conditions are met
        """
        if not cpr_levels:
            return True  # No CPR data, allow trade
        
        cpr_top = cpr_levels.get('cpr_top')
        cpr_bottom = cpr_levels.get('cpr_bottom')
        pivot = cpr_levels.get('pivot')
        
        if signal_type == 'bullish':
            # For bullish signals, price should be above CPR bottom
            return current_price > cpr_bottom if cpr_bottom else True
        elif signal_type == 'bearish':
            # For bearish signals, price should be below CPR top
            return current_price < cpr_top if cpr_top else True
        
        return True
    
    def get_cpr_strength(self, current_price, cpr_levels):
        """
        Calculate CPR strength (how close price is to CPR levels)
        
        Returns:
            float: Strength value (0-1, where 1 is strongest)
        """
        if not cpr_levels:
            return 0.5  # Neutral if no CPR data
        
        pivot = cpr_levels.get('pivot')
        cpr_top = cpr_levels.get('cpr_top')
        cpr_bottom = cpr_levels.get('cpr_bottom')
        
        if not all([pivot, cpr_top, cpr_bottom]):
            return 0.5
        
        # Calculate distance from pivot
        distance_from_pivot = abs(current_price - pivot)
        cpr_range = cpr_top - cpr_bottom
        
        if cpr_range == 0:
            return 0.5
        
        # Strength is inversely proportional to distance from pivot
        strength = 1 - (distance_from_pivot / cpr_range)
        return max(0, min(1, strength))  # Clamp between 0 and 1
    
    def clear_cache(self):
        """Clear CPR cache"""
        self.cpr_cache.clear()
        logger.info("CPR cache cleared")
    
    def get_cache_info(self):
        """Get cache information"""
        return {
            'cache_size': len(self.cpr_cache),
            'cache_keys': list(self.cpr_cache.keys())
        }

# Global instance
cpr_calculator = DynamicCPRCalculator() 