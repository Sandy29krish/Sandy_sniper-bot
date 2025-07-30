import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.nse_option_chain import nse_option_chain, get_current_expiry, get_next_expiry
from utils.kite_api import place_order
import json

logger = logging.getLogger(__name__)

class AutoRolloverManager:
    """
    Auto Rollover Manager for Monthly Options
    - Monitors expiry dates with 1 week buffer
    - Automatically rolls over positions to next month
    - Handles position transfer logic
    """
    
    def __init__(self):
        self.rollover_buffer_days = 7  # 1 week buffer
        self.rollover_state_file = "rollover_state.json"
        self.rollover_state = self._load_rollover_state()
        
    def check_rollover_required(self, symbol: str, current_expiry: str) -> bool:
        """
        Check if rollover is required based on 1 week buffer
        Returns: True if rollover needed, False otherwise
        """
        try:
            if not current_expiry:
                return False
            
            # Parse expiry date
            expiry_date = datetime.strptime(current_expiry, '%d-%b-%Y')
            current_date = datetime.now()
            
            # Calculate days to expiry
            days_to_expiry = (expiry_date - current_date).days
            
            logger.info(f"📅 {symbol} expiry check: {days_to_expiry} days remaining (Buffer: {self.rollover_buffer_days})")
            
            # Check if within rollover buffer
            if days_to_expiry <= self.rollover_buffer_days:
                logger.warning(f"⚠️ {symbol} rollover required! Only {days_to_expiry} days to expiry")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking rollover requirement for {symbol}: {e}")
            return False
    
    def execute_rollover(self, symbol: str, position_data: Dict) -> bool:
        """
        Execute rollover from current month to next month
        Returns: True if successful, False otherwise
        """
        try:
            logger.info(f"🔄 Starting rollover process for {symbol}")
            
            # Get current and next expiry dates
            current_expiry = get_current_expiry(symbol)
            next_expiry = get_next_expiry(symbol)
            
            if not current_expiry or not next_expiry:
                logger.error(f"❌ Could not get expiry dates for {symbol}")
                return False
            
            # Extract position details
            current_strike = position_data.get('strike_price', 0)
            option_type = position_data.get('option_type', '')  # CE or PE
            quantity = position_data.get('quantity', 0)
            signal_type = position_data.get('signal', '')
            
            logger.info(f"📊 Rolling over {symbol} {current_strike}{option_type} from {current_expiry} to {next_expiry}")
            
            # Step 1: Exit current month position
            exit_success = self._exit_current_position(symbol, position_data, current_expiry)
            if not exit_success:
                logger.error(f"❌ Failed to exit current position for {symbol}")
                return False
            
            # Step 2: Calculate new strike for next month (same 200 OTM logic)
            new_strike = self._calculate_rollover_strike(symbol, current_strike, option_type)
            
            # Step 3: Enter next month position
            entry_success = self._enter_next_month_position(
                symbol, new_strike, option_type, quantity, signal_type, next_expiry
            )
            
            if entry_success:
                # Update rollover state
                self._update_rollover_state(symbol, current_expiry, next_expiry, current_strike, new_strike)
                logger.info(f"✅ Rollover completed successfully for {symbol}")
                return True
            else:
                logger.error(f"❌ Failed to enter next month position for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error executing rollover for {symbol}: {e}")
            return False
    
    def _exit_current_position(self, symbol: str, position_data: Dict, current_expiry: str) -> bool:
        """Exit current month position"""
        try:
            strike_price = position_data.get('strike_price', 0)
            option_type = position_data.get('option_type', '')
            quantity = position_data.get('quantity', 0)
            signal_type = position_data.get('signal', '')
            
            # Create trading symbol for current month
            trading_symbol = self._create_trading_symbol(symbol, strike_price, option_type, current_expiry)
            
            # Place exit order (opposite of original entry)
            transaction_type = "SELL" if signal_type == "bullish" else "BUY"
            
            place_order(
                tradingsymbol=trading_symbol,
                exchange="NFO",
                quantity=quantity,
                transaction_type=transaction_type,
                product="NRML",
                order_type="MARKET"
            )
            
            logger.info(f"📤 Exited current position: {trading_symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exiting current position: {e}")
            return False
    
    def _enter_next_month_position(self, symbol: str, strike: int, option_type: str, 
                                  quantity: int, signal_type: str, next_expiry: str) -> bool:
        """Enter next month position"""
        try:
            # Create trading symbol for next month
            trading_symbol = self._create_trading_symbol(symbol, strike, option_type, next_expiry)
            
            # Place entry order (same as original entry)
            transaction_type = "BUY" if signal_type == "bullish" else "SELL"
            
            place_order(
                tradingsymbol=trading_symbol,
                exchange="NFO",
                quantity=quantity,
                transaction_type=transaction_type,
                product="NRML",
                order_type="MARKET"
            )
            
            logger.info(f"📥 Entered next month position: {trading_symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error entering next month position: {e}")
            return False
    
    def _calculate_rollover_strike(self, symbol: str, current_strike: int, option_type: str) -> int:
        """
        Calculate new strike price for rollover
        Maintains same 200 OTM logic relative to current futures price
        """
        try:
            # Get current futures price
            option_chain = nse_option_chain.get_option_chain(symbol)
            if not option_chain:
                # Fallback: use same strike
                return current_strike
            
            underlying_price = option_chain.get('underlyingValue', current_strike)
            
            # Calculate step size based on symbol
            if symbol == "BANKNIFTY":
                step = 100
            elif symbol == "NIFTY":
                step = 50
            elif symbol == "SENSEX":
                step = 100
            else:
                step = 50
            
            # Calculate 200 OTM strike
            if option_type == "CE":
                new_strike = ((underlying_price + step) // step) * step + 200
            else:  # PE
                new_strike = ((underlying_price - step) // step) * step - 200
            
            logger.info(f"📊 Rollover strike calculation: {symbol} {underlying_price} → {new_strike}{option_type}")
            return int(new_strike)
            
        except Exception as e:
            logger.error(f"❌ Error calculating rollover strike: {e}")
            return current_strike  # Fallback to current strike
    
    def _create_trading_symbol(self, symbol: str, strike: int, option_type: str, expiry: str) -> str:
        """Create trading symbol for option"""
        try:
            # Convert expiry format from 'DD-MMM-YYYY' to 'DDMMMYY'
            expiry_date = datetime.strptime(expiry, '%d-%b-%Y')
            expiry_formatted = expiry_date.strftime('%d%b%y').upper()
            
            # Create trading symbol
            trading_symbol = f"{symbol}{expiry_formatted}{strike}{option_type}"
            
            logger.info(f"🏷️ Created trading symbol: {trading_symbol}")
            return trading_symbol
            
        except Exception as e:
            logger.error(f"❌ Error creating trading symbol: {e}")
            return f"{symbol}{strike}{option_type}"
    
    def get_rollover_candidates(self, positions: Dict) -> List[str]:
        """
        Get list of positions that need rollover
        Returns: List of symbols requiring rollover
        """
        rollover_candidates = []
        
        try:
            for symbol, position_data in positions.items():
                current_expiry = position_data.get('expiry', '')
                
                if self.check_rollover_required(symbol, current_expiry):
                    rollover_candidates.append(symbol)
            
            if rollover_candidates:
                logger.info(f"🔄 Rollover candidates: {rollover_candidates}")
            
            return rollover_candidates
            
        except Exception as e:
            logger.error(f"❌ Error getting rollover candidates: {e}")
            return []
    
    def process_all_rollovers(self, positions: Dict) -> Dict:
        """
        Process rollovers for all eligible positions
        Returns: Updated positions dictionary
        """
        try:
            rollover_candidates = self.get_rollover_candidates(positions)
            updated_positions = positions.copy()
            
            for symbol in rollover_candidates:
                position_data = positions.get(symbol, {})
                
                rollover_success = self.execute_rollover(symbol, position_data)
                
                if rollover_success:
                    # Update position data with new expiry and strike
                    next_expiry = get_next_expiry(symbol)
                    new_strike = self._calculate_rollover_strike(
                        symbol, 
                        position_data.get('strike_price', 0), 
                        position_data.get('option_type', '')
                    )
                    
                    updated_positions[symbol].update({
                        'expiry': next_expiry,
                        'strike_price': new_strike,
                        'rollover_timestamp': datetime.now().isoformat(),
                        'rollover_count': position_data.get('rollover_count', 0) + 1
                    })
                    
                    logger.info(f"✅ Updated position data for {symbol} after rollover")
                else:
                    logger.error(f"❌ Rollover failed for {symbol}, position unchanged")
            
            return updated_positions
            
        except Exception as e:
            logger.error(f"❌ Error processing rollovers: {e}")
            return positions
    
    def _load_rollover_state(self) -> Dict:
        """Load rollover state from file"""
        try:
            with open(self.rollover_state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"❌ Error loading rollover state: {e}")
            return {}
    
    def _save_rollover_state(self):
        """Save rollover state to file"""
        try:
            with open(self.rollover_state_file, 'w') as f:
                json.dump(self.rollover_state, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving rollover state: {e}")
    
    def _update_rollover_state(self, symbol: str, old_expiry: str, new_expiry: str, 
                              old_strike: int, new_strike: int):
        """Update rollover state tracking"""
        try:
            rollover_record = {
                'timestamp': datetime.now().isoformat(),
                'old_expiry': old_expiry,
                'new_expiry': new_expiry,
                'old_strike': old_strike,
                'new_strike': new_strike
            }
            
            if symbol not in self.rollover_state:
                self.rollover_state[symbol] = []
            
            self.rollover_state[symbol].append(rollover_record)
            self._save_rollover_state()
            
            logger.info(f"📝 Updated rollover state for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error updating rollover state: {e}")
    
    def get_rollover_history(self, symbol: str = None) -> Dict:
        """Get rollover history for symbol or all symbols"""
        if symbol:
            return self.rollover_state.get(symbol, [])
        return self.rollover_state

# Global instance
auto_rollover_manager = AutoRolloverManager()

# Convenience functions
def check_and_process_rollovers(positions: Dict) -> Dict:
    """Check and process all required rollovers"""
    return auto_rollover_manager.process_all_rollovers(positions)

def is_rollover_required(symbol: str, expiry: str) -> bool:
    """Check if rollover is required for a position"""
    return auto_rollover_manager.check_rollover_required(symbol, expiry) 