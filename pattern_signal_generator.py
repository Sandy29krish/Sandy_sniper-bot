import numpy as np
import pandas as pd

class PatternSignalGenerator:
    def __init__(self, df):
        """
        df: pandas DataFrame with your candles and calculated indicators
        Expected columns include:
         - open, high, low, close, volume
         - ma3, ma9, ma20, ma50, ma200
         - rsi, rsi_ma9, rsi_ma14, rsi_ma26
         - lr_slope, pvi
         - cpr_top, cpr_bottom (optional)
        """
        self.df = df.copy()

    def detect_bullish_engulfing(self, i):
        """Bullish engulfing pattern at index i"""
        if i == 0:
            return False
        prev = self.df.iloc[i-1]
        curr = self.df.iloc[i]
        return (prev['close'] < prev['open']) and (curr['close'] > curr['open']) and \
               (curr['close'] > prev['open']) and (curr['open'] < prev['close'])

    def detect_bearish_engulfing(self, i):
        """Bearish engulfing pattern at index i"""
        if i == 0:
            return False
        prev = self.df.iloc[i-1]
        curr = self.df.iloc[i]
        return (prev['close'] > prev['open']) and (curr['close'] < curr['open']) and \
               (curr['open'] > prev['close']) and (curr['close'] < prev['open'])

    def detect_reversal_candle(self, i):
        """Simple check for reversal candle: bullish or bearish engulfing"""
        return self.detect_bullish_engulfing(i) or self.detect_bearish_engulfing(i)

    def check_entry_conditions(self, i):
        row = self.df.iloc[i]

        # MA Hierarchy
        bullish_ma = row['close'] > row['ma9'] > row['ma20'] > row['ma50'] > row['ma200']
        bearish_ma = row['close'] < row['ma9'] < row['ma20'] < row['ma50'] < row['ma200']

        # RSI Hierarchy
        bullish_rsi = row['rsi'] > row['rsi_ma26'] > row['rsi_ma14'] > row['rsi_ma9']
        bearish_rsi = row['rsi'] < row['rsi_ma26'] < row['rsi_ma14'] < row['rsi_ma9']

        # PVI and LR slope
        bullish_vol = row['pvi'] > 0 and row['lr_slope'] > 0
        bearish_vol = row['pvi'] < 0 and row['lr_slope'] < 0

        # CPR confirmation optional (True if missing)
        cpr_confirm = True
        if not np.isnan(row.get('cpr_top', np.nan)) and not np.isnan(row.get('cpr_bottom', np.nan)):
            if bullish_ma and row['close'] < row['cpr_bottom']:
                cpr_confirm = False
            if bearish_ma and row['close'] > row['cpr_top']:
                cpr_confirm = False

        if bullish_ma and bullish_rsi and bullish_vol and cpr_confirm:
            return "bullish"
        elif bearish_ma and bearish_rsi and bearish_vol and cpr_confirm:
            return "bearish"
        else:
            return None

    def check_exit_conditions(self, i):
        row = self.df.iloc[i]
        pos = self.df.iloc[i-1] if i > 0 else None

        # Exit if reversal candle detected
        if self.detect_reversal_candle(i):
            return True

        # Exit on adverse RSI cross (example)
        if pos is not None:
            if pos['rsi'] > pos['rsi_ma26'] and row['rsi'] < row['rsi_ma26']:
                return True
            if pos['rsi'] < pos['rsi_ma26'] and row['rsi'] > row['rsi_ma26']:
                return True

        # Exit on LR slope flattening or reversing
        if pos is not None and (pos['lr_slope'] * row['lr_slope'] < 0):
            return True

        return False

    def generate_signals(self):
        signals = []
        position = None  # 'bullish', 'bearish', or None
        for i in range(len(self.df)):
            entry_signal = self.check_entry_conditions(i)
            if position is None and entry_signal is not None:
                signals.append({'index': i, 'signal': 'enter_' + entry_signal})
                position = entry_signal
            elif position is not None:
                if self.check_exit_conditions(i):
                    signals.append({'index': i, 'signal': 'exit_' + position})
                    position = None
                else:
                    signals.append({'index': i, 'signal': 'hold_' + position})
            else:
                signals.append({'index': i, 'signal': 'no_action'})
        return signals