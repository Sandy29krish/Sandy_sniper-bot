import json
import os
from datetime import datetime

# Default log file path (overridable via environment)
LOG_FILE = os.getenv('TRADE_LOG_FILE', 'trade_log.json')

def log_trade(symbol, direction, lot_size, status, entry_price=None, exit_price=None, pnl=None):
    """
    Logs general trade data (used by expiry strategy).
    """
    trade_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'symbol': symbol,
        'direction': direction,
        'lot_size': lot_size,
        'status': status,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'pnl': pnl
    }
    trades = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                trades = []
    trades.append(trade_entry)
    with open(LOG_FILE, 'w') as f:
        json.dump(trades, f, indent=4)

def log_swing_trade(trade_data):
    """
    Logs swing trade entries with a timestamp to swing_trade_log.json
    """
    log_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'trade': trade_data
    }

    try:
        with open("swing_trade_log.json", "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"[❌] Error logging swing trade: {e}")
