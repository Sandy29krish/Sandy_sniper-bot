import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.kite_api import get_live_price, get_historical_data
from utils.kite_api import place_order
import time

logger = logging.getLogger(__name__)

class IntelligentOrderManager:
    """
    Intelligent Order Manager
    - Decides between MARKET vs LIMIT orders based on conditions
    - Uses AI analysis and market experience
    - Considers premium movement, volatility, urgency
    """
    
    def __init__(self):
        self.order_intelligence = {
            'volatility_threshold': 0.05,  # 5% volatility threshold
            'premium_spike_threshold': 0.15,  # 15% premium spike
            'market_order_scenarios': [
                'gap_adverse',      # Gap against position - immediate exit
                'stop_loss',        # Stop loss triggered - immediate exit
                'high_volatility',  # High volatility - quick execution
                'expiry_day',       # Expiry day - avoid slippage
                'friday_315'        # Friday 3:15 PM - forced exit
            ],
            'limit_order_scenarios': [
                'normal_entry',     # Normal entry conditions
                'profit_booking',   # Profit booking - can wait for better price
                'low_volatility',   # Low volatility - optimize price
                'premium_expensive' # Premium too high - wait for better price
            ]
        }
        
        # Order execution tracking for AI learning
        self.execution_history = []
        
    def decide_order_type(self, scenario: str, symbol: str, strike: str, 
                         current_premium: float, signal_strength: float = 0) -> Dict:
        """
        Intelligent decision between MARKET and LIMIT orders
        Returns: Dictionary with order_type, price, reasoning
        """
        try:
            logger.info(f"🧠 Analyzing order type for {symbol} {strike} in scenario: {scenario}")
            
            # Get market conditions
            market_conditions = self._analyze_market_conditions(symbol, current_premium)
            
            # AI-based decision logic
            decision = self._ai_order_decision(
                scenario, symbol, strike, current_premium, 
                signal_strength, market_conditions
            )
            
            logger.info(f"🎯 Order decision for {symbol}: {decision['order_type']} - {decision['reasoning']}")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Error in order type decision: {e}")
            # Fallback to MARKET order for safety
            return {
                'order_type': 'MARKET',
                'price': 0,
                'reasoning': f'Fallback to MARKET due to error: {str(e)}'
            }
    
    def _analyze_market_conditions(self, symbol: str, current_premium: float) -> Dict:
        """Analyze current market conditions"""
        try:
            # Get current price data
            current_price = get_live_price(symbol)
            if not current_price:
                return {'volatility': 'unknown', 'trend': 'unknown', 'volume': 'unknown'}
            
            # Simplified market condition analysis
            return {
                'volatility': 'medium',
                'trend': 'neutral', 
                'volume': 'normal',
                'current_price': current_price
            }
            
            # Determine volatility level
            if high_low_pct > 3.0:
                volatility = 'high'
            elif high_low_pct > 1.5:
                volatility = 'medium'
            else:
                volatility = 'low'
            
            # Determine trend (simplified)
            if ohlc_data['close'] > ohlc_data['open']:
                trend = 'bullish'
            elif ohlc_data['close'] < ohlc_data['open']:
                trend = 'bearish'
            else:
                trend = 'sideways'
            
            # Volume analysis (if available)
            volume_status = 'normal'  # Placeholder - can be enhanced
            
            conditions = {
                'volatility': volatility,
                'trend': trend,
                'volume': volume_status,
                'high_low_pct': high_low_pct,
                'current_time': datetime.now().time()
            }
            
            logger.info(f"📊 Market conditions for {symbol}: {conditions}")
            return conditions
            
        except Exception as e:
            logger.error(f"❌ Error analyzing market conditions: {e}")
            return {'volatility': 'unknown', 'trend': 'unknown', 'volume': 'unknown'}
    
    def _ai_order_decision(self, scenario: str, symbol: str, strike: str, 
                          current_premium: float, signal_strength: float, 
                          market_conditions: Dict) -> Dict:
        """AI-powered order type decision"""
        try:
            current_time = datetime.now().time()
            
            # MARKET ORDER scenarios (immediate execution needed)
            if scenario in self.order_intelligence['market_order_scenarios']:
                return self._market_order_decision(scenario, market_conditions)
            
            # Special time-based conditions
            if current_time >= datetime.strptime('15:15', '%H:%M').time():
                return {
                    'order_type': 'MARKET',
                    'price': 0,
                    'reasoning': 'Market order for Friday 3:15 PM or late day execution'
                }
            
            # High volatility = MARKET order (avoid slippage)
            if market_conditions.get('volatility') == 'high':
                return {
                    'order_type': 'MARKET',
                    'price': 0,
                    'reasoning': 'Market order due to high volatility - avoid slippage'
                }
            
            # Premium analysis for LIMIT vs MARKET
            premium_decision = self._analyze_premium_conditions(
                current_premium, signal_strength, market_conditions
            )
            
            if premium_decision:
                return premium_decision
            
            # Default logic based on signal strength and conditions
            return self._default_order_logic(signal_strength, market_conditions)
            
        except Exception as e:
            logger.error(f"❌ Error in AI order decision: {e}")
            return {
                'order_type': 'MARKET',
                'price': 0,
                'reasoning': f'Fallback to MARKET due to AI error: {str(e)}'
            }
    
    def _market_order_decision(self, scenario: str, market_conditions: Dict) -> Dict:
        """Decision logic for MARKET order scenarios"""
        reasoning_map = {
            'gap_adverse': 'MARKET order for immediate exit due to adverse gap',
            'stop_loss': 'MARKET order for immediate stop loss execution',
            'high_volatility': 'MARKET order due to high market volatility',
            'expiry_day': 'MARKET order on expiry day to avoid time decay',
            'friday_315': 'MARKET order for mandatory Friday 3:15 PM exit'
        }
        
        return {
            'order_type': 'MARKET',
            'price': 0,
            'reasoning': reasoning_map.get(scenario, 'MARKET order for immediate execution')
        }
    
    def _analyze_premium_conditions(self, current_premium: float, signal_strength: float, 
                                   market_conditions: Dict) -> Optional[Dict]:
        """Analyze premium conditions for order type decision"""
        try:
            # If premium is very high, consider LIMIT order to get better price
            if current_premium > 200:  # High premium threshold
                if market_conditions.get('volatility') == 'low':
                    limit_price = current_premium * 0.98  # 2% below current price
                    return {
                        'order_type': 'LIMIT',
                        'price': round(limit_price, 2),
                        'reasoning': f'LIMIT order at ₹{limit_price} - premium too high (₹{current_premium}), low volatility allows price optimization'
                    }
            
            # If premium is reasonable and signal is very strong, use MARKET
            if signal_strength >= 8.5 and current_premium <= 150:
                return {
                    'order_type': 'MARKET',
                    'price': 0,
                    'reasoning': f'MARKET order for SUPER STRONG signal ({signal_strength}/10) with reasonable premium (₹{current_premium})'
                }
            
            # If premium is low and volatility is low, use LIMIT for better entry
            if current_premium <= 50 and market_conditions.get('volatility') == 'low':
                limit_price = current_premium * 1.02  # 2% above current price
                return {
                    'order_type': 'LIMIT',
                    'price': round(limit_price, 2),
                    'reasoning': f'LIMIT order at ₹{limit_price} - low premium allows price optimization'
                }
            
            return None  # No specific premium-based decision
            
        except Exception as e:
            logger.error(f"❌ Error analyzing premium conditions: {e}")
            return None
    
    def _default_order_logic(self, signal_strength: float, market_conditions: Dict) -> Dict:
        """Default order type logic"""
        try:
            # Super strong signals with good conditions = MARKET
            if signal_strength >= 9.0:
                return {
                    'order_type': 'MARKET',
                    'price': 0,
                    'reasoning': f'MARKET order for SUPER STRONG signal ({signal_strength}/10)'
                }
            
            # Strong signals in low volatility = LIMIT for better price
            if signal_strength >= 7.0 and market_conditions.get('volatility') == 'low':
                return {
                    'order_type': 'LIMIT',
                    'price': 'calculate_on_execution',  # Will be calculated during execution
                    'reasoning': f'LIMIT order for STRONG signal ({signal_strength}/10) in low volatility'
                }
            
            # Default to MARKET for reliability
            return {
                'order_type': 'MARKET',
                'price': 0,
                'reasoning': 'Default MARKET order for reliable execution'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in default order logic: {e}")
            return {
                'order_type': 'MARKET',
                'price': 0,
                'reasoning': 'Fallback MARKET order due to logic error'
            }
    
    def execute_intelligent_order(self, tradingsymbol: str, exchange: str, quantity: int,
                                 transaction_type: str, scenario: str, symbol: str,
                                 current_premium: float = 0, signal_strength: float = 0) -> bool:
        """Execute order with intelligent type selection"""
        try:
            # Get intelligent order decision
            order_decision = self.decide_order_type(
                scenario, symbol, tradingsymbol, current_premium, signal_strength
            )
            
            order_type = order_decision['order_type']
            limit_price = order_decision.get('price', 0)
            reasoning = order_decision['reasoning']
            
            # Execute the order
            if order_type == 'MARKET':
                success = place_order(
                    tradingsymbol=tradingsymbol,
                    exchange=exchange,
                    quantity=quantity,
                    transaction_type=transaction_type,
                    product="NRML",
                    order_type="MARKET"
                )
                
            else:  # LIMIT order
                if limit_price == 'calculate_on_execution':
                    # Calculate limit price based on current market price
                    current_price = get_live_price(symbol)
                    if transaction_type == 'BUY':
                        limit_price = current_price * 1.005  # 0.5% above market
                    else:
                        limit_price = current_price * 0.995  # 0.5% below market
                    limit_price = round(limit_price, 2)
                
                success = place_order(
                    tradingsymbol=tradingsymbol,
                    exchange=exchange,
                    quantity=quantity,
                    transaction_type=transaction_type,
                    product="NRML",
                    order_type="LIMIT",
                    price=limit_price
                )
            
            # Log execution for AI learning
            self._log_execution(tradingsymbol, order_type, reasoning, success)
            
            logger.info(f"🎯 Intelligent order executed: {tradingsymbol} {order_type} - {reasoning}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Error executing intelligent order: {e}")
            return False
    
    def _log_execution(self, tradingsymbol: str, order_type: str, reasoning: str, success: bool):
        """Log order execution for AI learning"""
        try:
            execution_record = {
                'timestamp': datetime.now().isoformat(),
                'tradingsymbol': tradingsymbol,
                'order_type': order_type,
                'reasoning': reasoning,
                'success': success
            }
            
            self.execution_history.append(execution_record)
            
            # Keep only last 100 records for memory management
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
                
        except Exception as e:
            logger.error(f"❌ Error logging execution: {e}")
    
    def get_execution_analytics(self) -> Dict:
        """Get execution analytics for AI learning"""
        try:
            if not self.execution_history:
                return {'total_orders': 0, 'success_rate': 0, 'market_vs_limit': {}}
            
            total_orders = len(self.execution_history)
            successful_orders = sum(1 for record in self.execution_history if record['success'])
            success_rate = successful_orders / total_orders
            
            # Market vs Limit analysis
            market_orders = sum(1 for record in self.execution_history if record['order_type'] == 'MARKET')
            limit_orders = sum(1 for record in self.execution_history if record['order_type'] == 'LIMIT')
            
            analytics = {
                'total_orders': total_orders,
                'success_rate': round(success_rate * 100, 2),
                'market_orders': market_orders,
                'limit_orders': limit_orders,
                'market_success_rate': self._calculate_type_success_rate('MARKET'),
                'limit_success_rate': self._calculate_type_success_rate('LIMIT')
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error calculating execution analytics: {e}")
            return {'total_orders': 0, 'success_rate': 0}
    
    def _calculate_type_success_rate(self, order_type: str) -> float:
        """Calculate success rate for specific order type"""
        try:
            type_orders = [record for record in self.execution_history if record['order_type'] == order_type]
            if not type_orders:
                return 0.0
            
            successful = sum(1 for record in type_orders if record['success'])
            return round((successful / len(type_orders)) * 100, 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculating type success rate: {e}")
            return 0.0

# Global instance
intelligent_order_manager = IntelligentOrderManager()

# Convenience functions
def execute_smart_order(tradingsymbol: str, exchange: str, quantity: int,
                       transaction_type: str, scenario: str, symbol: str,
                       current_premium: float = 0, signal_strength: float = 0) -> bool:
    """Execute order with intelligent type selection"""
    return intelligent_order_manager.execute_intelligent_order(
        tradingsymbol, exchange, quantity, transaction_type, 
        scenario, symbol, current_premium, signal_strength
    )

def get_order_analytics() -> Dict:
    """Get order execution analytics"""
    return intelligent_order_manager.get_execution_analytics() 