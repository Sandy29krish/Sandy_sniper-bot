import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import pytz

class ZerodhaDataIndicators:
    def __init__(self, api_key, access_token):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.ist = pytz.timezone("Asia/Kolkata")

    def fetch_historical_data(self, instrument_token, from_date, to_date, interval="30minute"):
        # from_date, to_date: datetime.date or datetime.datetime objects
        # returns pandas DataFrame with columns: date, open, high, low, close, volume

        from_str = from_date.strftime("%Y-%m-%d %H:%M:%S")
        to_str = to_date.strftime("%Y-%m-%d %H:%M:%S")
        data = self.kite.historical_data(instrument_token, from_str, to_str, interval)

        df = pd.DataFrame(data)
        if df.empty:
            return df

        # Ensure datetime index with IST timezone
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize('UTC').dt.tz_convert(self.ist)
        df.set_index('date', inplace=True)
        return df

    def calculate_typical_price(self, df):
        df['typical_price'] = (df['high'] + df['low'] + df['close'] + df['open']) / 4
        return df

    def calculate_mas(self, df):
        # Weighted MA(200) of high
        df['ma200'] = df['high'].rolling(window=200).apply(
            lambda x: np.average(x, weights=np.arange(1, 201)), raw=True)

        # EMA(50) of high
        df['ma50'] = df['high'].ewm(span=50, adjust=False).mean()

        # EMA(9) of typical price
        df['ma9'] = df['typical_price'].ewm(span=9, adjust=False).mean()

        # SMA(20) of typical price
        df['ma20'] = df['typical_price'].rolling(window=20).mean()

        # SMA(3) of typical price
        df['ma3'] = df['typical_price'].rolling(window=3).mean()
        return df

    def calculate_rsi(self, df, period=14):
        delta = df['typical_price'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # RSI MAs
        df['rsi_ma9'] = df['rsi'].rolling(window=9).mean()
        df['rsi_ma14'] = df['rsi'].rolling(window=14).mean()
        df['rsi_ma26'] = df['rsi'].rolling(window=26).mean()
        return df

    def calculate_lr_slope(self, df, period=21):
        slopes = []
        for i in range(len(df)):
            if i < period:
                slopes.append(np.nan)
                continue
            y = df['high'].iloc[i-period:i]
            x = np.arange(period)
            coeffs = np.polyfit(x, y, 1)
            slopes.append(coeffs[0])
        df['lr_slope'] = slopes
        return df

    def calculate_pvi(self, df):
        pvi = [np.nan]
        for i in range(1, len(df)):
            if df['volume'].iloc[i] > df['volume'].iloc[i-1]:
                pvi.append(pvi[-1] + ((df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]) * 100)
            else:
                pvi.append(pvi[-1])
        df['pvi'] = pvi
        return df

    def calculate_cpr(self, df):
        # Placeholder: you can add actual CPR calc here using pivot points if available
        df['cpr_top'] = np.nan
        df['cpr_bottom'] = np.nan
        return df

    def get_indicators(self, instrument_token, from_date, to_date, interval="30minute"):
        df = self.fetch_historical_data(instrument_token, from_date, to_date, interval)
        if df.empty:
            return df
        df = self.calculate_typical_price(df)
        df = self.calculate_mas(df)
        df = self.calculate_rsi(df)
        df = self.calculate_lr_slope(df)
        df = self.calculate_pvi(df)
        df = self.calculate_cpr(df)
        return df