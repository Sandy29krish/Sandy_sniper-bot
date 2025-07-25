# utils/lot_manager.py

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
