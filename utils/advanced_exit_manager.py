import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from utils.indicators import fetch_data, calculate_linear_regression_slope
from utils.kite_api import get_historical_data

logger = logging.getLogger(__name__)

class AdvancedExitManager:
    """
    USER'S EXACT EXIT CONDITIONS IMPLEMENTATION:
    
    BULLISH EXITS:
    1. 15min cross below 20sma
    2. Volume decrease drastically 
    3. LR slope forms negative divergence or moves below Zero
    4. Book partial profit at swing high and rest on another high
    5. AI finds weakening momentum
    
    BEARISH EXITS:
    - Opposite conditions (15min cross above 20sma, etc.)
    """
    
    def __init__(self):
        self.partial_profit_taken = {}  # Track partial profits per symbol
        self.swing_high_tracker = {}    # Track swing highs per symbol
        self.volume_baseline = {}       # Track normal volume levels
        self.lr_slope_history = {}      # Track LR slope for divergence
        
        # Exit thresholds
        self.volume_drop_threshold = 0.4  # 60% volume drop
        self.swing_high_lookback = 5     # Periods to look for swing high
        self.divergence_periods = 3      # Periods for divergence detection
        
    def check_all_exit_conditions(self, symbol, position_data):
        """
        Check USER'S EXACT exit conditions
        Returns: (should_exit, exit_reason, exit_type, quantity_to_exit)
        """
        try:
            # Get 15min and 30min data for analysis
            df_15m = fetch_data(symbol, interval="15minute", days=2)
            if df_15m is None or len(df_15m) < 25:
                return False, None, None, 0
            
            current_price = df_15m['close'].iloc[-1]
            entry_price = position_data.get('entry_price', 0)
            signal_type = position_data.get('signal', '')
            total_quantity = position_data.get('quantity', 0)
            
            if entry_price <= 0 or total_quantity <= 0:
                return False, None, None, 0
            
            # Calculate profit/loss
            if signal_type == 'bullish':
                profit_pct = (current_price - entry_price) / entry_price * 100
            else:
                profit_pct = (entry_price - current_price) / entry_price * 100
            
            # Initialize tracking for this symbol
            if symbol not in self.partial_profit_taken:
                self.partial_profit_taken[symbol] = False
                self.swing_high_tracker[symbol] = []
                self.volume_baseline[symbol] = df_15m['volume'].rolling(20).mean().iloc[-1]
                self.lr_slope_history[symbol] = []
            
            # 1. Check for SWING HIGH partial profit opportunity
            swing_exit = self._check_swing_high_exit(df_15m, symbol, signal_type, profit_pct)
            if swing_exit[0]:
                return swing_exit
            
            # 2. Check 15min vs 20 SMA cross
            sma_cross_exit = self._check_sma_cross_exit(df_15m, signal_type)
            if sma_cross_exit[0]:
                return sma_cross_exit + (total_quantity,)  # Full exit
            
            # 3. Check volume decrease
            volume_exit = self._check_volume_decrease(df_15m, symbol)
            if volume_exit[0]:
                return volume_exit + (total_quantity,)  # Full exit
            
            # 4. Check LR slope divergence/negative zone
            lr_slope_exit = self._check_lr_slope_conditions(df_15m, symbol, signal_type, current_price, profit_pct)
            if lr_slope_exit[0]:
                return lr_slope_exit + (total_quantity,)  # Full exit
            
            # 5. Check AI momentum weakening
            ai_momentum_exit = self._check_ai_momentum_weakness(df_15m, position_data)
            if ai_momentum_exit[0]:
                return ai_momentum_exit + (total_quantity,)  # Full exit
            
            return False, None, None, 0
            
        except Exception as e:
            logger.error(f"Error in exit condition check for {symbol}: {e}")
            return False, None, None, 0
    
    def _check_swing_high_exit(self, df_15m, symbol, signal_type, profit_pct):
        """Check for swing high to book partial profits"""
        try:
            closes = df_15m['close'].values
            highs = df_15m['high'].values
            lows = df_15m['low'].values
            
            # Detect swing high/low based on signal type
            if signal_type == 'bullish':
                # Look for swing high (local maximum)
                if len(highs) >= self.swing_high_lookback:
                    recent_highs = highs[-self.swing_high_lookback:]
                    current_high = highs[-1]
                    
                    # Check if current high is higher than previous highs
                    is_swing_high = current_high == max(recent_highs)
                    
                    # Only take partial profit if we're in profit and haven't taken partial yet
                    if is_swing_high and profit_pct > 5 and not self.partial_profit_taken[symbol]:
                        self.partial_profit_taken[symbol] = True
                        self.swing_high_tracker[symbol].append({
                            'price': current_high,
                            'time': df_15m.index[-1],
                            'profit_pct': profit_pct
                        })
                        
                        # Take 50% profit at swing high
                        partial_quantity = int(df_15m.iloc[0].get('quantity', 0) * 0.5)
                        return True, f"Swing High detected at ₹{current_high:.1f} (Profit: {profit_pct:.1f}%)", "partial_profit", partial_quantity
            
            else:  # Bearish signal
                # Look for swing low (local minimum) for bearish positions
                if len(lows) >= self.swing_high_lookback:
                    recent_lows = lows[-self.swing_high_lookback:]
                    current_low = lows[-1]
                    
                    # Check if current low is lower than previous lows
                    is_swing_low = current_low == min(recent_lows)
                    
                    if is_swing_low and profit_pct > 5 and not self.partial_profit_taken[symbol]:
                        self.partial_profit_taken[symbol] = True
                        self.swing_high_tracker[symbol].append({
                            'price': current_low,
                            'time': df_15m.index[-1],
                            'profit_pct': profit_pct
                        })
                        
                        # Take 50% profit at swing low
                        partial_quantity = int(df_15m.iloc[0].get('quantity', 0) * 0.5)
                        return True, f"Swing Low detected at ₹{current_low:.1f} (Profit: {profit_pct:.1f}%)", "partial_profit", partial_quantity
            
            return False, None, None, 0
            
        except Exception as e:
            logger.error(f"Error checking swing high for {symbol}: {e}")
            return False, None, None, 0
    
    def _check_sma_cross_exit(self, df_15m, signal_type):
        """Check 15min price cross below/above 20 SMA"""
        try:
            # Calculate 20 SMA
            df_15m['sma_20'] = df_15m['close'].rolling(window=20).mean()
            
            if len(df_15m) < 2:
                return False, None, None
            
            current_price = df_15m['close'].iloc[-1]
            prev_price = df_15m['close'].iloc[-2]
            current_sma = df_15m['sma_20'].iloc[-1]
            prev_sma = df_15m['sma_20'].iloc[-2]
            
            if signal_type == 'bullish':
                # Exit if price crosses below 20 SMA
                cross_below = (prev_price >= prev_sma) and (current_price < current_sma)
                if cross_below:
                    return True, f"15min cross below 20 SMA (₹{current_price:.1f} < ₹{current_sma:.1f})", "sma_cross"
            
            else:  # Bearish
                # Exit if price crosses above 20 SMA  
                cross_above = (prev_price <= prev_sma) and (current_price > current_sma)
                if cross_above:
                    return True, f"15min cross above 20 SMA (₹{current_price:.1f} > ₹{current_sma:.1f})", "sma_cross"
            
            return False, None, None
            
        except Exception as e:
            logger.error(f"Error checking SMA cross: {e}")
            return False, None, None
    
    def _check_volume_decrease(self, df_15m, symbol):
        """Check for drastic volume decrease"""
        try:
            if len(df_15m) < 10:
                return False, None, None
            
            current_volume = df_15m['volume'].iloc[-1]
            avg_volume = self.volume_baseline[symbol]
            
            # Check if current volume is significantly lower
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio < self.volume_drop_threshold:
                drop_pct = (1 - volume_ratio) * 100
                return True, f"Volume decreased drastically ({drop_pct:.0f}% drop)", "volume_decrease"
            
            return False, None, None
            
        except Exception as e:
            logger.error(f"Error checking volume decrease: {e}")
            return False, None, None
    
    def _check_lr_slope_conditions(self, df_15m, symbol, signal_type, current_price, profit_pct):
        """Check LR slope negative divergence or zero crossing"""
        try:
            # Calculate LR slope for recent periods
            lr_slope = calculate_linear_regression_slope(df_15m['close'], periods=21)
            
            if lr_slope is None:
                return False, None, None
            
            current_lr_slope = lr_slope.iloc[-1]
            
            # Track LR slope history for divergence detection
            self.lr_slope_history[symbol].append({
                'slope': current_lr_slope,
                'price': current_price,
                'profit': profit_pct
            })
            
            # Keep only recent history
            if len(self.lr_slope_history[symbol]) > 10:
                self.lr_slope_history[symbol] = self.lr_slope_history[symbol][-10:]
            
            if signal_type == 'bullish':
                # Exit conditions for bullish positions:
                # 1. LR slope moves below zero (negative zone)
                if current_lr_slope < 0:
                    return True, f"LR Slope entered negative zone ({current_lr_slope:.4f})", "lr_slope_negative"
                
                # 2. Negative divergence (price higher but LR slope lower)
                if len(self.lr_slope_history[symbol]) >= self.divergence_periods:
                    recent_data = self.lr_slope_history[symbol][-self.divergence_periods:]
                    
                    price_trend = recent_data[-1]['price'] > recent_data[0]['price']  # Price going up
                    slope_trend = recent_data[-1]['slope'] < recent_data[0]['slope']  # Slope going down
                    
                    if price_trend and slope_trend and profit_pct > 3:  # Negative divergence
                        return True, f"LR Slope negative divergence detected", "lr_slope_divergence"
            
            else:  # Bearish
                # Exit conditions for bearish positions:
                # 1. LR slope moves above zero (positive zone)
                if current_lr_slope > 0:
                    return True, f"LR Slope entered positive zone ({current_lr_slope:.4f})", "lr_slope_positive"
                
                # 2. Positive divergence (price lower but LR slope higher)
                if len(self.lr_slope_history[symbol]) >= self.divergence_periods:
                    recent_data = self.lr_slope_history[symbol][-self.divergence_periods:]
                    
                    price_trend = recent_data[-1]['price'] < recent_data[0]['price']  # Price going down
                    slope_trend = recent_data[-1]['slope'] > recent_data[0]['slope']  # Slope going up
                    
                    if price_trend and slope_trend and profit_pct > 3:  # Positive divergence
                        return True, f"LR Slope positive divergence detected", "lr_slope_divergence"
            
            return False, None, None
            
        except Exception as e:
            logger.error(f"Error checking LR slope conditions: {e}")
            return False, None, None
    
    def _check_ai_momentum_weakness(self, df_15m, position_data):
        """Check if AI detects weakening momentum"""
        try:
            # Import AI assistant for momentum analysis
            from utils.ai_assistant import AIAssistant
            ai = AIAssistant()
            
            # Prepare recent data for AI analysis
            recent_data = {
                'close_prices': df_15m['close'].tail(10).tolist(),
                'volumes': df_15m['volume'].tail(10).tolist(),
                'highs': df_15m['high'].tail(10).tolist(),
                'lows': df_15m['low'].tail(10).tolist(),
                'signal_type': position_data.get('signal', ''),
                'entry_time': position_data.get('entry_time', ''),
                'entry_price': position_data.get('entry_price', 0)
            }
            
            # Get AI momentum analysis
            momentum_strength = ai.analyze_momentum_strength(recent_data)
            
            # Exit if AI detects significant momentum weakness
            if momentum_strength < 0.3:  # 30% threshold for momentum weakness
                confidence_pct = momentum_strength * 100
                return True, f"AI detected weakening momentum (Confidence: {confidence_pct:.0f}%)", "ai_momentum_weak"
            
            return False, None, None
            
        except Exception as e:
            logger.error(f"Error in AI momentum analysis: {e}")
            return False, None, None
    
    def reset_partial_profit_status(self, symbol):
        """Reset partial profit status when position is fully closed"""
        if symbol in self.partial_profit_taken:
            self.partial_profit_taken[symbol] = False
            self.swing_high_tracker[symbol] = []
            self.lr_slope_history[symbol] = []
    
    def get_exit_summary(self, symbol):
        """Get summary of exit conditions for reporting"""
        if symbol not in self.swing_high_tracker:
            return "No exit tracking data available"
        
        summary = []
        if self.partial_profit_taken[symbol]:
            swing_data = self.swing_high_tracker[symbol][-1] if self.swing_high_tracker[symbol] else None
            if swing_data:
                summary.append(f"✅ Partial profit taken at swing high ₹{swing_data['price']:.1f} (+{swing_data['profit_pct']:.1f}%)")
        
        return "\n".join(summary) if summary else "No partial profits taken yet" 