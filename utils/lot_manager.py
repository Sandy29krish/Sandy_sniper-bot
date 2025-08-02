# utils/lot_manager.py

import logging
import json
import os
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class DynamicLotManager:
    """
    Dynamic lot scaling manager with 2x minimum and 5x maximum scaling
    based on win rate and profit factor performance
    """
    
    def __init__(self):
        self.performance_file = "lot_scaling_performance.json"
        self.performance_data = {
            'total_trades': 0,
            'successful_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 1.0,
            'current_scaling_factor': 2.0,  # Start with 2x minimum
            'trade_history': []
        }
        self.load_performance_data()
    
    def load_performance_data(self):
        """Load performance data from file"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    self.performance_data.update(data)
                logger.info(f"Loaded lot scaling performance: Win Rate {self.performance_data['win_rate']*100:.1f}%, Scaling Factor {self.performance_data['current_scaling_factor']:.1f}x")
        except Exception as e:
            logger.error(f"Error loading lot scaling performance: {e}")
    
    def save_performance_data(self):
        """Save performance data to file"""
        try:
            with open(self.performance_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving lot scaling performance: {e}")
    
    def calculate_dynamic_lot_size(self, max_risk, stop_loss_percent, option_price, base_lot_size):
        """
        Calculate dynamic lot size with 2x minimum, 5x maximum scaling
        based on performance metrics
        """
        try:
            # Calculate base lots using traditional risk management
            stop_loss_amount = option_price * (stop_loss_percent / 100)
            max_options = max_risk / stop_loss_amount if stop_loss_amount > 0 else 1
            base_lots = max(1, int(max_options / base_lot_size))
            
            # Cap base lots to reasonable maximum (10 lots)
            base_lots = min(base_lots, 10)
            
            # Apply dynamic scaling factor
            scaling_factor = self.get_current_scaling_factor()
            scaled_lots = int(base_lots * scaling_factor)
            
            # Enforce minimum 2 lots and maximum 5x base lots or 50 lots, whichever is smaller
            min_lots = max(2, base_lots * 2)  # Minimum 2 lots or 2x base lots
            max_lots = min(base_lots * 5, 50)  # Maximum 5x base lots or 50 lots
            
            final_lots = max(min_lots, min(scaled_lots, max_lots))
            
            logger.info(f"Dynamic lot calculation: Base={base_lots}, Scaling Factor={scaling_factor:.1f}x, Final={final_lots} lots")
            
            return final_lots
            
        except Exception as e:
            logger.error(f"Error in dynamic lot calculation: {e}")
            return 2  # Default to 2 lots (minimum)
    
    def get_current_scaling_factor(self):
        """
        Calculate current scaling factor based on performance
        Range: 2.0x (minimum) to 5.0x (maximum)
        """
        try:
            win_rate = self.performance_data['win_rate']
            profit_factor = self.performance_data['profit_factor']
            
            # Base scaling starts at 2.0
            base_scaling = 2.0
            
            # Win rate contribution (0.0 to 1.5)
            # 60%+ win rate gets full bonus, below 40% gets penalty
            if win_rate >= 0.6:
                win_rate_bonus = 1.5
            elif win_rate >= 0.5:
                win_rate_bonus = 1.0 + (win_rate - 0.5) * 5  # Linear scaling from 1.0 to 1.5
            elif win_rate >= 0.4:
                win_rate_bonus = 0.5 + (win_rate - 0.4) * 5  # Linear scaling from 0.5 to 1.0
            else:
                win_rate_bonus = 0.0  # Below 40% win rate
            
            # Profit factor contribution (0.0 to 1.5)
            # PF >= 2.0 gets full bonus, PF < 1.0 gets penalty
            if profit_factor >= 2.0:
                pf_bonus = 1.5
            elif profit_factor >= 1.2:
                pf_bonus = 0.5 + (profit_factor - 1.2) * 1.25  # Linear scaling
            elif profit_factor >= 1.0:
                pf_bonus = (profit_factor - 1.0) * 2.5  # Linear scaling from 0.0 to 0.5
            else:
                pf_bonus = 0.0  # Below 1.0 profit factor
            
            # Calculate final scaling factor
            scaling_factor = base_scaling + win_rate_bonus + pf_bonus
            
            # Ensure bounds (2.0 to 5.0)
            scaling_factor = max(2.0, min(5.0, scaling_factor))
            
            # Update current scaling factor
            self.performance_data['current_scaling_factor'] = scaling_factor
            
            return scaling_factor
            
        except Exception as e:
            logger.error(f"Error calculating scaling factor: {e}")
            return 2.0  # Default to minimum scaling
    
    def update_performance(self, trade_result):
        """
        Update performance metrics based on trade result
        """
        try:
            # Add trade to history
            self.performance_data['trade_history'].append({
                'timestamp': datetime.now().isoformat(),
                'success': trade_result.get('success', False),
                'profit': trade_result.get('profit', 0),
                'lots_used': trade_result.get('lots_used', 2)
            })
            
            # Keep only last 100 trades for performance calculation
            if len(self.performance_data['trade_history']) > 100:
                self.performance_data['trade_history'] = self.performance_data['trade_history'][-100:]
            
            # Update overall metrics
            self.performance_data['total_trades'] += 1
            if trade_result.get('success', False):
                self.performance_data['successful_trades'] += 1
            
            # Calculate win rate
            if self.performance_data['total_trades'] > 0:
                self.performance_data['win_rate'] = self.performance_data['successful_trades'] / self.performance_data['total_trades']
            
            # Calculate profit factor from recent trade history
            recent_trades = self.performance_data['trade_history']
            if len(recent_trades) >= 10:  # Need at least 10 trades for meaningful calculation
                profits = [t['profit'] for t in recent_trades if t['profit'] > 0]
                losses = [abs(t['profit']) for t in recent_trades if t['profit'] < 0]
                
                if profits and losses:
                    avg_profit = np.mean(profits)
                    avg_loss = np.mean(losses)
                    self.performance_data['profit_factor'] = avg_profit / avg_loss if avg_loss > 0 else 1.0
                elif profits and not losses:
                    self.performance_data['profit_factor'] = 5.0  # Perfect profit factor
                else:
                    self.performance_data['profit_factor'] = 0.1  # Poor performance
            
            # Recalculate scaling factor
            new_scaling_factor = self.get_current_scaling_factor()
            
            # Save updated data
            self.save_performance_data()
            
            logger.info(f"Lot scaling updated: Win Rate {self.performance_data['win_rate']*100:.1f}%, "
                       f"Profit Factor {self.performance_data['profit_factor']:.2f}, "
                       f"New Scaling Factor {new_scaling_factor:.1f}x")
            
        except Exception as e:
            logger.error(f"Error updating lot scaling performance: {e}")
    
    def get_performance_summary(self):
        """Get current performance summary for reporting"""
        try:
            return {
                'total_trades': self.performance_data['total_trades'],
                'win_rate': f"{self.performance_data['win_rate']*100:.1f}%",
                'profit_factor': f"{self.performance_data['profit_factor']:.2f}",
                'current_scaling': f"{self.performance_data['current_scaling_factor']:.1f}x",
                'scaling_range': "2.0x - 5.0x",
                'recent_trades': len(self.performance_data['trade_history'])
            }
        except:
            return {'error': 'Performance summary unavailable'}

# Initialize global instance
dynamic_lot_manager = DynamicLotManager()

def calculate_lot_size(max_risk, stop_loss_percent, option_price, lot_size):
    """Enhanced lot size calculation with dynamic scaling"""
    try:
        return dynamic_lot_manager.calculate_dynamic_lot_size(
            max_risk, stop_loss_percent, option_price, lot_size
        )
    except Exception as e:
        logger.error(f"Error in enhanced lot calculation: {e}")
        return 2  # Fallback to minimum 2 lots

def update_lot_performance(trade_result):
    """Update lot scaling performance"""
    try:
        dynamic_lot_manager.update_performance(trade_result)
    except Exception as e:
        logger.error(f"Error updating lot performance: {e}")

def get_lot_scaling_summary():
    """Get lot scaling performance summary"""
    return dynamic_lot_manager.get_performance_summary()

def get_swing_strike(symbol, future_price, direction):
    """
    Returns next 200 points OTM strike for swing trade.
    """
    if symbol == "BANKNIFTY":
        step = 100
    elif symbol == "NIFTY":
        step = 50
    elif symbol == "SENSEX":
        step = 100
    else:
        step = 50

    if direction == "CE":
        strike = ((future_price + step) // step) * step + 200
    else:
        strike = ((future_price - step) // step) * step - 200

    return strike
