import logging
from datetime import datetime

class PositionMonitor:
    def __init__(self):
        self.active_positions = {}

    def add_position(self, symbol, direction, entry_price, lot_size):
        self.active_positions[symbol] = {
            'direction': direction,
            'entry_price': entry_price,
            'lot_size': lot_size,
            'entry_time': datetime.utcnow()
        }
        logging.info(f"Position added: {symbol} {direction} at {entry_price} for {lot_size} lots")

    def remove_position(self, symbol):
        if symbol in self.active_positions:
            del self.active_positions[symbol]
            logging.info(f"Position removed: {symbol}")

    def get_positions(self):
        return self.active_positions

    def update_pnl(self, symbol, current_price):
        if symbol not in self.active_positions:
            return None
        pos = self.active_positions[symbol]
        direction = pos['direction']
        entry_price = pos['entry_price']
        lot_size = pos['lot_size']
        if direction == 'bullish':
            pnl = (current_price - entry_price) * lot_size
        else:
            pnl = (entry_price - current_price) * lot_size
        return pnl
