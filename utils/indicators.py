import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.kite_api import get_kite_instance
from utils.nse_data import SYMBOL_TOKEN_MAP

def calculate_mas(df):
    df['ma9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()
    df['ma200'] = df['high'].rolling(200).mean()  # 200 WMA based on High
    return df

def calculate_rsi(df, period=21):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    df['rsi_ma9'] = df['rsi'].rolling(9).mean()
    df['rsi_ma14'] = df['rsi'].rolling(14).mean()
    df['rsi_ma26'] = df['rsi'].rolling(26).mean()
    return df

def calculate_lr_slope(df, period=21):
    slopes = []
    for i in range(len(df)):
        if i < period:
            slopes.append(np.nan)
        else:
            y = df['close'].iloc[i - period:i]
            x = np.arange(period)
            b, m = np.polyfit(x, y, 1)
            slopes.append(m)
    df['lr_slope'] = slopes
    return df

def calculate_pvi(df):
    pvi = [1000]
    for i in range(1, len(df)):
        if df['volume'].iloc[i] > df['volume'].iloc[i - 1]:
            change = ((df['close'].iloc[i] - df['close'].iloc[i - 1]) / df['close'].iloc[i - 1])
            pvi.append(pvi[-1] * (1 + change))
        else:
            pvi.append(pvi[-1])
    df['pvi'] = pvi
    return df

def fetch_data(symbol, interval="15minute", days=3):
    kite = get_kite_instance()
    token = SYMBOL_TOKEN_MAP.get(symbol)
    if not token:
        print(f"Unknown token for {symbol}")
        return None

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    try:
        data = kite.historical_data(token, from_date, to_date, interval)
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def get_indicators_15m_30m(symbol):
    df_15m = fetch_data(symbol, interval="15minute", days=3)
    df_30m = fetch_data(symbol, interval="30minute", days=5)

    if df_30m is None or df_30m.empty:
        return None, {}

    # 15m analysis for early strength detection (optional use later)
    # df_15m = calculate_mas(df_15m)
    # df_15m = calculate_rsi(df_15m)
    # df_15m = calculate_lr_slope(df_15m)
    # df_15m = calculate_pvi(df_15m)

    # 30m final signal confirmation
    df = df_30m.copy()
    df = calculate_mas(df)
    df = calculate_rsi(df)
    df = calculate_lr_slope(df)
    df = calculate_pvi(df)

    last = df.iloc[-1]

    # Conditions
    ma_hierarchy = last['close'] > last['ma9'] > last['ma20'] > last['ma50'] > last['ma200']
    rsi_strong = last['rsi'] > last['rsi_ma26']
    rsi_hierarchy = last['rsi'] > last['rsi_ma26'] > last['rsi_ma14'] > last['rsi_ma9']
    pvi_positive = last['pvi'] > df['pvi'].iloc[-2]
    lr_slope_positive = last['lr_slope'] > 0

    signal = None
    if ma_hierarchy and rsi_strong and pvi_positive and lr_slope_positive:
        signal = "bullish"
    elif not ma_hierarchy and rsi_hierarchy and not pvi_positive and not lr_slope_positive:
        signal = "bearish"

    indicators = {
        "rsi": last['rsi'],
        "rsi_ma26": last['rsi_ma26'],
        "rsi_ma14": last['rsi_ma14'],
        "rsi_ma9": last['rsi_ma9'],
        "ma_hierarchy": ma_hierarchy,
        "pvi_positive": pvi_positive,
        "lr_slope_positive": lr_slope_positive,
        "rsi_strong": rsi_strong
    }

    return signal, indicators
