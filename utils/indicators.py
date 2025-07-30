import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.kite_api import get_kite_instance
from utils.nse_data import SYMBOL_TOKEN_MAP
from utils.cpr_calculator import cpr_calculator

def calculate_mas(df):
    df['ma9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()
    df['ma200'] = df['high'].rolling(200).mean()  # 200 WMA based on High
    return df

def calculate_rsi(df, period=21):  # Changed to 21 to match chart RSI(21,ohlc/4)
    # Calculate OHLC/4 (typical price) as used in your charts
    df['ohlc4'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    # Calculate RSI on OHLC/4 instead of close
    delta = df['ohlc4'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Calculate moving averages on RSI as shown in your charts
    df['rsi_ma9'] = df['rsi'].rolling(9).mean()
    df['rsi_ma14'] = df['rsi'].rolling(14).mean()
    df['rsi_ma26'] = df['rsi'].rolling(26).mean()
    return df

def calculate_lr_slope(df, period=21):
    """
    Calculate Linear Regression Slope on High prices (21,H) as shown in charts
    """
    slopes = []
    for i in range(len(df)):
        if i < period:
            slopes.append(np.nan)
        else:
            # Use High prices instead of Close prices to match chart LR Slope (21,H)
            y = df['high'].iloc[i - period:i]
            x = np.arange(period)
            b, m = np.polyfit(x, y, 1)
            slopes.append(m)
    df['lr_slope'] = slopes
    return df

def calculate_linear_regression_slope(series, periods=21):
    """
    Calculate Linear Regression Slope for a pandas Series
    Used by exit manager for momentum analysis
    """
    slopes = []
    for i in range(len(series)):
        if i < periods:
            slopes.append(np.nan)
        else:
            x = np.arange(periods)
            y = series.iloc[i - periods:i].values
            slope, _ = np.polyfit(x, y, 1)
            slopes.append(slope)
    
    return pd.Series(slopes, index=series.index)

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

def get_live_cpr_data(symbol):
    """
    Get live CPR data for a symbol using Zerodha Kite API
    """
    try:
        # Get live CPR levels
        multi_cpr = cpr_calculator.get_multi_timeframe_cpr(symbol)
        
        if 'intraday' in multi_cpr:
            return multi_cpr['intraday']
        else:
            print(f"No live CPR data available for {symbol}")
            return None
            
    except Exception as e:
        print(f"Error getting live CPR data for {symbol}: {e}")
        return None

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

    # 30m final signal confirmation with live CPR
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

    # Live CPR validation - OPTIONAL (lower priority)
    cpr_validation = True  # Default to True so it doesn't block signals
    cpr_support = False
    live_cpr = get_live_cpr_data(symbol)
    
    if live_cpr:
        current_price = last['close']
        cpr_top = live_cpr.get('cpr_top')
        cpr_bottom = live_cpr.get('cpr_bottom')
        
        if ma_hierarchy and rsi_strong and cpr_bottom:  # Bullish conditions
            cpr_support = current_price > cpr_bottom  # Just track if CPR supports
        elif not ma_hierarchy and rsi_hierarchy and cpr_top:  # Bearish conditions
            cpr_support = current_price < cpr_top  # Just track if CPR supports

    # Core signal generation (4 main conditions - CPR is bonus)
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
        "rsi_strong": rsi_strong,
        "cpr_validation": cpr_validation,
        "cpr_support": cpr_support,  # Track if CPR supports the signal
        "live_cpr": live_cpr  # Include live CPR data
    }

    return signal, indicators
