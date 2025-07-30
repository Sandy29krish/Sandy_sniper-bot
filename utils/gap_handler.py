import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.secure_kite_api import get_live_price, get_historical_data
from utils.kite_api import place_order

logger = logging.getLogger(__name__)

class GapHandler:
    """
    Smart Gap Handling System
    - Gap AGAINST position → Square off immediately (reduce loss)
    - Gap FAVORING position → Book profits at highs (maximize profit)
    - Immediate action triggers for gap scenarios
    """
    
    def __init__(self):
        self.gap_threshold = 2.0  # 2% gap threshold
        self.favorable_gap_profit_targets = {
            'immediate_booking': 0.08,  # 8% immediate profit booking
            'trail_stop': 0.05,         # 5% trailing stop from high
            'maximum_hold': 0.15        # 15% maximum profit before full exit
        }
        
    def detect_gap_scenarios(self, positions: Dict) -> List[Dict]:
        """
        Detect gap scenarios for all active positions
        Returns: List of gap scenarios requiring action
        """
        gap_scenarios = []
        
        try:
            for symbol, position_data in positions.items():
                gap_info = self._analyze_gap_for_position(symbol, position_data)
                
                if gap_info and gap_info['requires_action']:
                    gap_scenarios.append(gap_info)
                    logger.info(f"🚨 Gap detected for {symbol}: {gap_info['gap_type']} ({gap_info['gap_percentage']:.2f}%)")
            
            return gap_scenarios
            
        except Exception as e:
            logger.error(f"❌ Error detecting gap scenarios: {e}")
            return []
    
    def _analyze_gap_for_position(self, symbol: str, position_data: Dict) -> Optional[Dict]:
        """Analyze gap scenario for a specific position"""
        try:
            # Get previous day's closing price and current price
            prev_close = self._get_previous_close(symbol)
            current_price = get_live_price(symbol)
            
            if not prev_close or not current_price:
                return None
            
            # Calculate gap percentage
            gap_percentage = ((current_price - prev_close) / prev_close) * 100
            
            # Check if gap exceeds threshold
            if abs(gap_percentage) < self.gap_threshold:
                return None  # No significant gap
            
            # Determine gap direction and impact on position
            signal_type = position_data.get('signal', '')
            entry_price = position_data.get('entry_price', 0)
            
            # Calculate current profit/loss
            if signal_type == 'bullish':
                current_pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:
                current_pnl_pct = ((entry_price - current_price) / entry_price) * 100
            
            # Determine gap impact
            gap_impact = self._determine_gap_impact(gap_percentage, signal_type)
            
            return {
                'symbol': symbol,
                'gap_percentage': gap_percentage,
                'gap_type': 'gap_up' if gap_percentage > 0 else 'gap_down',
                'gap_impact': gap_impact,  # 'favorable' or 'adverse'
                'current_pnl_pct': current_pnl_pct,
                'signal_type': signal_type,
                'requires_action': True,
                'recommended_action': self._get_recommended_action(gap_impact, current_pnl_pct),
                'urgency': 'high' if gap_impact == 'adverse' else 'medium',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing gap for {symbol}: {e}")
            return None
    
    def _determine_gap_impact(self, gap_percentage: float, signal_type: str) -> str:
        """Determine if gap is favorable or adverse to position"""
        if signal_type == 'bullish':
            # For bullish positions: gap up is favorable, gap down is adverse
            return 'favorable' if gap_percentage > 0 else 'adverse'
        elif signal_type == 'bearish':
            # For bearish positions: gap down is favorable, gap up is adverse
            return 'favorable' if gap_percentage < 0 else 'adverse'
        else:
            return 'neutral'
    
    def _get_recommended_action(self, gap_impact: str, current_pnl_pct: float) -> str:
        """Get recommended action based on gap impact"""
        if gap_impact == 'adverse':
            return 'square_off_immediately'
        elif gap_impact == 'favorable':
            if current_pnl_pct >= 8.0:  # Already profitable
                return 'book_profits_at_high'
            else:
                return 'monitor_for_profit_booking'
        else:
            return 'no_action'
    
    def execute_gap_actions(self, gap_scenarios: List[Dict], positions: Dict) -> Dict:
        """
        Execute appropriate actions for all gap scenarios
        Returns: Updated positions dictionary
        """
        updated_positions = positions.copy()
        
        try:
            for gap_info in gap_scenarios:
                symbol = gap_info['symbol']
                action = gap_info['recommended_action']
                
                if action == 'square_off_immediately':
                    success = self._execute_immediate_square_off(symbol, positions[symbol])
                    if success:
                        # Remove position from active positions
                        updated_positions.pop(symbol, None)
                        logger.info(f"✅ Squared off {symbol} due to adverse gap")
                
                elif action == 'book_profits_at_high':
                    success = self._execute_profit_booking(symbol, positions[symbol], gap_info)
                    if success:
                        # Update position with profit booking info
                        updated_positions[symbol]['gap_profit_booked'] = True
                        updated_positions[symbol]['gap_booking_timestamp'] = datetime.now().isoformat()
                        logger.info(f"✅ Booked profits for {symbol} on favorable gap")
                
                elif action == 'monitor_for_profit_booking':
                    # Set up trailing stop for favorable gap
                    self._setup_trailing_stop(symbol, updated_positions[symbol], gap_info)
                    logger.info(f"📊 Set up trailing stop for {symbol} on favorable gap")
            
            return updated_positions
            
        except Exception as e:
            logger.error(f"❌ Error executing gap actions: {e}")
            return positions
    
    def _execute_immediate_square_off(self, symbol: str, position_data: Dict) -> bool:
        """Execute immediate square off for adverse gap"""
        try:
            strike = position_data.get('strike', '')
            quantity = position_data.get('quantity', 0)
            signal_type = position_data.get('signal', '')
            
            # Place opposite order to square off
            transaction_type = "SELL" if signal_type == "bullish" else "BUY"
            
            place_order(
                tradingsymbol=strike,
                exchange="NFO",
                quantity=quantity,
                transaction_type=transaction_type,
                product="NRML",
                order_type="MARKET"
            )
            
            logger.info(f"🚨 ADVERSE GAP SQUARE OFF: {symbol} {strike} {quantity} units")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing immediate square off for {symbol}: {e}")
            return False
    
    def _execute_profit_booking(self, symbol: str, position_data: Dict, gap_info: Dict) -> bool:
        """Execute profit booking for favorable gap"""
        try:
            strike = position_data.get('strike', '')
            quantity = position_data.get('quantity', 0)
            signal_type = position_data.get('signal', '')
            current_pnl_pct = gap_info.get('current_pnl_pct', 0)
            
            # Determine booking quantity based on profit level
            if current_pnl_pct >= 15.0:
                # Book 100% if profit >= 15%
                booking_quantity = quantity
            elif current_pnl_pct >= 10.0:
                # Book 75% if profit >= 10%
                booking_quantity = int(quantity * 0.75)
            else:
                # Book 50% if profit >= 8%
                booking_quantity = int(quantity * 0.50)
            
            # Place booking order
            transaction_type = "SELL" if signal_type == "bullish" else "BUY"
            
            place_order(
                tradingsymbol=strike,
                exchange="NFO",
                quantity=booking_quantity,
                transaction_type=transaction_type,
                product="NRML",
                order_type="MARKET"
            )
            
            logger.info(f"💰 FAVORABLE GAP PROFIT BOOKING: {symbol} {booking_quantity}/{quantity} units at {current_pnl_pct:.1f}% profit")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing profit booking for {symbol}: {e}")
            return False
    
    def _setup_trailing_stop(self, symbol: str, position_data: Dict, gap_info: Dict):
        """Setup trailing stop for favorable gap monitoring"""
        try:
            current_price = get_live_price(symbol)
            if not current_price:
                return
            
            # Set trailing stop parameters
            trailing_stop_data = {
                'enabled': True,
                'trigger_price': current_price,
                'trail_percentage': self.favorable_gap_profit_targets['trail_stop'],
                'max_profit_target': self.favorable_gap_profit_targets['maximum_hold'],
                'gap_triggered': True,
                'setup_timestamp': datetime.now().isoformat()
            }
            
            position_data['trailing_stop'] = trailing_stop_data
            logger.info(f"📈 Trailing stop setup for {symbol}: Trail={trailing_stop_data['trail_percentage']*100}%")
            
        except Exception as e:
            logger.error(f"❌ Error setting up trailing stop for {symbol}: {e}")
    
    def _get_previous_close(self, symbol: str) -> Optional[float]:
        """Get previous day's closing price"""
        try:
            # Get historical data for last 2 days
            historical_data = get_historical_data(symbol, interval="day", days=2)
            
            if historical_data and len(historical_data) >= 2:
                # Return previous day's close (second last entry)
                prev_close = historical_data.iloc[-2]['close']
                logger.info(f"📊 Previous close for {symbol}: ₹{prev_close}")
                return prev_close
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting previous close for {symbol}: {e}")
            return None
    
    def monitor_gap_positions(self, positions: Dict) -> Dict:
        """
        Continuous monitoring of gap-affected positions
        Returns: Updated positions with gap monitoring
        """
        try:
            updated_positions = positions.copy()
            
            for symbol, position_data in positions.items():
                # Check if position has trailing stop due to favorable gap
                trailing_stop = position_data.get('trailing_stop', {})
                
                if trailing_stop.get('enabled', False) and trailing_stop.get('gap_triggered', False):
                    # Monitor trailing stop
                    stop_triggered = self._check_trailing_stop(symbol, position_data)
                    
                    if stop_triggered:
                        # Execute trailing stop exit
                        success = self._execute_trailing_stop_exit(symbol, position_data)
                        if success:
                            updated_positions.pop(symbol, None)
                            logger.info(f"✅ Trailing stop executed for {symbol}")
            
            return updated_positions
            
        except Exception as e:
            logger.error(f"❌ Error monitoring gap positions: {e}")
            return positions
    
    def _check_trailing_stop(self, symbol: str, position_data: Dict) -> bool:
        """Check if trailing stop should be triggered"""
        try:
            trailing_stop = position_data.get('trailing_stop', {})
            current_price = get_live_price(symbol)
            trigger_price = trailing_stop.get('trigger_price', 0)
            trail_percentage = trailing_stop.get('trail_percentage', 0.05)
            
            if not current_price or not trigger_price:
                return False
            
            # Calculate trailing stop price
            signal_type = position_data.get('signal', '')
            
            if signal_type == 'bullish':
                # For bullish: trigger if price drops by trail_percentage from high
                stop_price = trigger_price * (1 - trail_percentage)
                return current_price <= stop_price
            else:
                # For bearish: trigger if price rises by trail_percentage from low
                stop_price = trigger_price * (1 + trail_percentage)
                return current_price >= stop_price
            
        except Exception as e:
            logger.error(f"❌ Error checking trailing stop for {symbol}: {e}")
            return False
    
    def _execute_trailing_stop_exit(self, symbol: str, position_data: Dict) -> bool:
        """Execute trailing stop exit"""
        try:
            strike = position_data.get('strike', '')
            quantity = position_data.get('quantity', 0)
            signal_type = position_data.get('signal', '')
            
            # Place exit order
            transaction_type = "SELL" if signal_type == "bullish" else "BUY"
            
            place_order(
                tradingsymbol=strike,
                exchange="NFO",
                quantity=quantity,
                transaction_type=transaction_type,
                product="NRML",
                order_type="MARKET"
            )
            
            logger.info(f"🛑 TRAILING STOP EXIT: {symbol} {strike} {quantity} units")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing trailing stop exit for {symbol}: {e}")
            return False
    
    def get_gap_summary(self, gap_scenarios: List[Dict]) -> Dict:
        """Get summary of gap scenarios"""
        try:
            if not gap_scenarios:
                return {'total_gaps': 0, 'adverse_gaps': 0, 'favorable_gaps': 0}
            
            adverse_gaps = sum(1 for gap in gap_scenarios if gap['gap_impact'] == 'adverse')
            favorable_gaps = sum(1 for gap in gap_scenarios if gap['gap_impact'] == 'favorable')
            
            return {
                'total_gaps': len(gap_scenarios),
                'adverse_gaps': adverse_gaps,
                'favorable_gaps': favorable_gaps,
                'gap_details': gap_scenarios
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating gap summary: {e}")
            return {'total_gaps': 0, 'adverse_gaps': 0, 'favorable_gaps': 0}

# Global instance
gap_handler = GapHandler()

# Convenience functions
def detect_and_handle_gaps(positions: Dict) -> Dict:
    """Detect and handle all gap scenarios"""
    gap_scenarios = gap_handler.detect_gap_scenarios(positions)
    if gap_scenarios:
        return gap_handler.execute_gap_actions(gap_scenarios, positions)
    return positions

def monitor_gap_affected_positions(positions: Dict) -> Dict:
    """Monitor positions affected by gaps"""
    return gap_handler.monitor_gap_positions(positions) 