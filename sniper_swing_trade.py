import logging
import datetime
import pytz

logging.basicConfig(filename='swing_bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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


class SniperSwingBot:
    def __init__(self):
        self.positions = []
        self.active = False
        # For demonstration, set some example CPR and trend values
        self.cpr_level = 90  # example CPR level
        self.ma20 = 95       # example 20 MA value
        self.trend = 'uptrend'  # or 'downtrend'

    def get_price_mas(self):
        # Fetch current price and MAs: 9, 20, 50, 200 WMA
        # Placeholder: Replace with actual data fetching code
        return {'price': 100, 'ma9': 95, 'ma20': self.ma20, 'ma50': 85, 'ma200': 80}

    def get_prev_close(self):
        # Placeholder for previous candle close price, replace with real data fetch
        return 98

    def get_rsi_values(self):
        return {'rsi21': 65, 'rsi_ma26': 60, 'rsi_ma14': 58, 'rsi_ma9': 55}

    def get_price_volume_indicator(self):
        return True  # True means volume increasing or positive divergence

    def get_lr_slope(self):
        return True  # True means slope > 0 or positive divergence

    def price_rejected_above_cpr(self):
        # Placeholder for price rejected above CPR near 200WMA (optional bonus)
        return False

    def bullish_entry_conditions(self):
        mas = self.get_price_mas()
        rsi = self.get_rsi_values()
        pvi = self.get_price_volume_indicator()
        lr = self.get_lr_slope()
        cpr_reject = self.price_rejected_above_cpr()

        prev_close = self.get_prev_close()
        current_price = mas['price']

        # Determine CPR direction for swing_cpr_signal
        direction = 'down_to_cpr' if prev_close > self.cpr_level else 'up_to_cpr'
        cpr_signal = swing_cpr_signal(current_price, prev_close, self.cpr_level, direction)

        # MA rejection check (using 20 MA and current trend)
        ma_signal = swing_ma_signal(current_price, prev_close, mas['ma20'], self.trend)

        # Entry rules for bullish
        cond1 = mas['price'] > mas['ma9'] > mas['ma20'] > mas['ma50'] > mas['ma200']
        cond2 = rsi['rsi21'] > rsi['rsi_ma26'] > rsi['rsi_ma14'] > rsi['rsi_ma9']
        cond3 = pvi
        cond4 = lr
        cond5 = cpr_signal in ('bullish_continuation', 'bullish_breakout') or ma_signal == 'bullish_continuation'

        logging.info(f"Checking bullish entry: {cond1=}, {cond2=}, {cond3=}, {cond4=}, CPR Signal={cpr_signal}, MA Signal={ma_signal}")

        # All four primary conditions must be true and at least one CPR or MA bullish confirmation
        return cond1 and cond2 and cond3 and cond4 and cond5

    def bearish_entry_conditions(self):
        mas = self.get_price_mas()
        rsi = self.get_rsi_values()
        pvi = self.get_price_volume_indicator()
        lr = self.get_lr_slope()
        cpr_reject = self.price_rejected_above_cpr()

        prev_close = self.get_prev_close()
        current_price = mas['price']

        direction = 'up_to_cpr' if prev_close < self.cpr_level else 'down_to_cpr'
        cpr_signal = swing_cpr_signal(current_price, prev_close, self.cpr_level, direction)

        ma_signal = swing_ma_signal(current_price, prev_close, mas['ma20'], self.trend)

        cond1 = mas['price'] < mas['ma9'] < mas['ma20'] < mas['ma50'] < mas['ma200']
        cond2 = rsi['rsi21'] < rsi['rsi_ma26'] < rsi['rsi_ma14'] < rsi['rsi_ma9']
        cond3 = pvi  # Should be volume decreasing or negative divergence in real impl.
        cond4 = lr   # Should be LR slope negative or negative divergence in real impl.
        cond5 = cpr_signal in ('bearish_continuation', 'bearish_breakdown') or ma_signal == 'bearish_continuation'

        logging.info(f"Checking bearish entry: {cond1=}, {cond2=}, {cond3=}, {cond4=}, CPR Signal={cpr_signal}, MA Signal={ma_signal}")

        return cond1 and cond2 and cond3 and cond4 and cond5

    def bullish_exit_conditions(self):
        logging.info("Checking bullish exit conditions...")
        return False  # Replace with your exit logic

    def bearish_exit_conditions(self):
        logging.info("Checking bearish exit conditions...")
        return False  # Replace with your exit logic

    def run(self):
        logging.info("Sniper Swing Bot running...")

        position = self.positions[-1] if self.positions else None

        if position == 'bull':
            if self.bullish_exit_conditions():
                self.exit_trade()
        elif position == 'bear':
            if self.bearish_exit_conditions():
                self.exit_trade()
        else:
            if self.bullish_entry_conditions():
                self.enter_trade('bull')
            elif self.bearish_entry_conditions():
                self.enter_trade('bear')

    def enter_trade(self, direction):
        logging.info(f"Entering {direction} trade.")
        print(f"Entered {direction} trade (demo).")
        self.positions.append(direction)
        # Add Zerodha order execution here

    def exit_trade(self):
        logging.info("Exiting trade.")
        print("Exited trade (demo).")
        if self.positions:
            self.positions.pop()
        # Add Zerodha order exit here

    def force_exit_all(self):
        logging.info("Force exiting all positions.")
        self.positions.clear()
        print("Forced exit of all positions.")
