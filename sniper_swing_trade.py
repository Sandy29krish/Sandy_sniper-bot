import logging
from datetime import datetime
from utils.indicators import calculate_mas, calculate_rsi, calculate_lr_slope, calculate_pvi
from utils.nse_data import fetch_live_price_by_token
from utils.trade_logger import log_trade
from utils.telegram_bot import send_telegram_message
from utils.swing_config import SWING_CONFIG

logging.basicConfig(
    filename='swing_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def swing_cpr_signal(current_price, prev_price, cpr_level, direction):
    if direction == 'down_to_cpr':
        if prev_price > cpr_level and current_price <= cpr_level:
            return 'testing_cpr_support'
        elif prev_price <= cpr_level and current_price > cpr_level:
            return 'bullish_continuation'
        elif prev_price > cpr_level and current_price < cpr_level:
            return 'bearish_breakdown'
    elif direction == 'up_to_cpr':
        if prev_price < cpr_level and current_price >= cpr_level:
            return 'testing_cpr_resistance'
        elif prev_price >= cpr_level and current_price < cpr_level:
            return 'bearish_continuation'
        elif prev_price < cpr_level and current_price > cpr_level:
            return 'bullish_breakout'
    return 'no_signal'


def swing_ma_signal(current_price, prev_price, ma_level, trend):
    if trend == 'uptrend':
        if prev_price > ma_level and current_price <= ma_level:
            return 'testing_support'
        elif prev_price <= ma_level and current_price > ma_level:
            return 'bullish_continuation'
    elif trend == 'downtrend':
        if prev_price < ma_level and current_price >= ma_level:
            return 'testing_resistance'
        elif prev_price >= ma_level and current_price < ma_level:
            return 'bearish_continuation'
    return 'no_signal'


class SniperSwing:
    def __init__(self, capital, config):
        self.positions = {}
        self.capital = capital
        self.config = config
        self.prev_closes = {symbol_key: None for symbol_key in config.keys()}

    def fetch_data(self, symbol_key):
        conf = self.config[symbol_key]
        token = conf['instrument_token']
        exchange = conf['exchange']
        price_data = fetch_live_price_by_token(token, exchange)
        mas = calculate_mas(price_data)
        rsi = calculate_rsi(price_data)
        lr_slope = calculate_lr_slope(price_data)
        pvi = calculate_pvi(price_data)
        return price_data['close'], mas, rsi, lr_slope, pvi

    def check_entry_conditions(self, symbol_key):
        current_price, mas, rsi, lr_slope, pvi = self.fetch_data(symbol_key)
        prev_close = self.prev_closes.get(symbol_key)
        conf = self.config[symbol_key]
        if prev_close is None:
            self.prev_closes[symbol_key] = current_price
            return False
        direction = 'down_to_cpr' if prev_close > conf['cpr_level'] else 'up_to_cpr'
        cpr_signal = swing_cpr_signal(current_price, prev_close, conf['cpr_level'], direction)
        ma_signal = swing_ma_signal(current_price, prev_close, mas['ma20'], conf['trend'])
        bullish_conditions = (
            current_price > mas['ma9'] > mas['ma20'] > mas['ma50'] > mas['ma200'] and
            rsi['rsi21'] > rsi['rsi_ma26'] > rsi['rsi_ma14'] > rsi['rsi_ma9'] and
            pvi and
            lr_slope and
            (cpr_signal in ['bullish_continuation', 'bullish_breakout'] or ma_signal == 'bullish_continuation')
        )
        bearish_conditions = (
            current_price < mas['ma9'] < mas['ma20'] < mas['ma50'] < mas['ma200'] and
            rsi['rsi21'] < rsi['rsi_ma26'] < rsi['rsi_ma14'] < rsi['rsi_ma9'] and
            not pvi and
            not lr_slope and
            (cpr_signal in ['bearish_continuation', 'bearish_breakdown'] or ma_signal == 'bearish_continuation')
        )
        logging.info(f"{conf['full_name']} Entry Check - Bullish: {bullish_conditions}, Bearish: {bearish_conditions}, CPR: {cpr_signal}, MA: {ma_signal}")
        self.prev_closes[symbol_key] = current_price
        if bullish_conditions:
            return 'bullish'
        elif bearish_conditions:
            return 'bearish'
        else:
            return False

    def enter_trade(self, symbol_key, direction):
        conf = self.config[symbol_key]
        lot_size = conf['lot_size']
        full_name = conf['full_name']
        logging.info(f"Entering {direction} trade on {full_name} with lot size {lot_size}")
        send_telegram_message(f"✅ Entering {direction} swing trade on {full_name}, Lot size: {lot_size}")
        # TODO: Zerodha API order placement here
        self.positions[symbol_key] = {'direction': direction, 'entry_time': datetime.now()}

    def check_exit_conditions(self, symbol_key):
        # TODO: Implement your exit conditions here
        return False

    def exit_trade(self, symbol_key):
        if symbol_key not in self.positions:
            return
        conf = self.config[symbol_key]
        direction = self.positions[symbol_key]['direction']
        full_name = conf['full_name']
        logging.info(f"Exiting {direction} trade on {full_name}")
        send_telegram_message(f"❌ Exiting {direction} swing trade on {full_name}")
        # TODO: Zerodha order exit here
        del self.positions[symbol_key]

    def run(self):
        logging.info("Running Sniper Swing multi-symbol iteration")
        for symbol_key in self.config.keys():
            position = self.positions.get(symbol_key)
            if position:
                if self.check_exit_conditions(symbol_key):
                    self.exit_trade(symbol_key)
            else:
                direction = self.check_entry_conditions(symbol_key)
                if direction:
                    self.enter_trade(symbol_key, direction)
