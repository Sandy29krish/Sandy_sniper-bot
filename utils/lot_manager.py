# utils/lot_manager.py

def calculate_lot_size(max_risk, stop_loss_percent, option_price, lot_size):
    """Calculate number of lots based on risk management"""
    try:
        # Calculate stop loss amount per option
        stop_loss_amount = option_price * (stop_loss_percent / 100)
        
        # Calculate maximum number of options we can buy
        max_options = max_risk / stop_loss_amount
        
        # Calculate number of lots (round down to whole lots)
        lots = int(max_options / lot_size)
        
        # Ensure minimum 1 lot, maximum 10 lots for safety
        return max(1, min(lots, 10))
    except Exception as e:
        return 1  # Default to 1 lot on error

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
