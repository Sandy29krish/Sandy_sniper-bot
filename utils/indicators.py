#!/usr/bin/env python3
"""
Technical Indicators for Sandy Sniper Bot - Enhanced Edition
Preserves your original settings and core logic
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.kite_api import get_kite_instance
from utils.nse_data import SYMBOL_TOKEN_MAP
from utils.cpr_calculator import cpr_calculator
import logging

logger = logging.getLogger(__name__)

# ======= YOUR ORIGINAL CORE INDICATORS (Enhanced) =======

def calculate_sma(close_series, period=20):
    """Calculate Simple Moving Average"""
    try:
        sma = close_series.rolling(window=period).mean()
        logger.debug(f"SMA({period}) calculated: Latest value = {sma.iloc[-1]:.2f}")
        return sma
    except Exception as e:
        logger.error(f"Error calculating SMA: {e}")
        return pd.Series(index=close_series.index, dtype=float)

def calculate_ema(close_series, period=20, ai_adjustment=None, symbol=None):
    """Calculate Exponential Moving Average with AI adjustment tracking"""
    try:
        original_ema = close_series.ewm(span=period, adjust=False).mean()
        
        # Apply AI adjustment if provided
        if ai_adjustment and ai_adjustment.get('enabled', False):
            from utils.ai_assistant import AIAssistant
            ai = AIAssistant()
            
            adjustment_factor = ai_adjustment.get('factor', 1.0)
            adjustment_reason = ai_adjustment.get('reason', 'Market conditions optimization')
            
            if adjustment_factor != 1.0:
                adjusted_ema = original_ema * adjustment_factor
                
                # Log the AI modification
                ai.log_indicator_modification(
                    indicator_name=f'EMA({period})',
                    old_value=float(original_ema.iloc[-1]),
                    new_value=float(adjusted_ema.iloc[-1]),
                    reason=adjustment_reason,
                    symbol=symbol
                )
                
                logger.info(f"AI adjusted EMA({period}) for {symbol}: {original_ema.iloc[-1]:.2f} -> {adjusted_ema.iloc[-1]:.2f} (Factor: {adjustment_factor})")
                return adjusted_ema
        
        logger.debug(f"EMA({period}) calculated: Latest value = {original_ema.iloc[-1]:.2f}")
        return original_ema
    except Exception as e:
        logger.error(f"Error calculating EMA: {e}")
        return pd.Series(index=close_series.index, dtype=float)

def calculate_rsi(df, period=21, ai_adjustment=None, symbol=None):
    """Calculate RSI using your original OHLC/4 method - Enhanced with AI tracking"""
    try:
        # Your original OHLC/4 calculation
        df['ohlc4'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        
        # Calculate RSI on OHLC/4 instead of close (your original method)
        delta = df['ohlc4'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        original_rsi = 100 - (100 / (1 + rs))
        
        # Apply AI adjustment if provided
        if ai_adjustment and ai_adjustment.get('enabled', False):
            from utils.ai_assistant import AIAssistant
            ai = AIAssistant()
            
            adjustment_type = ai_adjustment.get('type', 'threshold')
            adjustment_reason = ai_adjustment.get('reason', 'Market volatility optimization')
            
            if adjustment_type == 'threshold':
                # Adjust RSI thresholds (70/30 -> dynamic based on market conditions)
                volatility_factor = ai_adjustment.get('volatility_factor', 1.0)
                
                # Original RSI remains the same, but interpretation changes
                adjusted_rsi = original_rsi.copy()
                
                # Log the threshold adjustment
                old_threshold = f"70/30"
                new_threshold = f"{70 * volatility_factor:.0f}/{30 / volatility_factor:.0f}"
                
                ai.log_indicator_modification(
                    indicator_name=f'RSI({period})',
                    old_value=70.0,
                    new_value=70.0 * volatility_factor,
                    reason=f"{adjustment_reason} - Threshold adjustment from {old_threshold} to {new_threshold}",
                    symbol=symbol
                )
                
                logger.info(f"AI adjusted RSI({period}) thresholds for {symbol}: {old_threshold} -> {new_threshold}")
                return adjusted_rsi
        
        logger.debug(f"RSI calculated: Latest value = {original_rsi.iloc[-1]:.2f}")
        return original_rsi
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return pd.Series(index=df.index, dtype=float)

def calculate_macd(close_series, fast=12, slow=26, signal=9):
    """Calculate MACD with your enhanced logic"""
    try:
        # Your MACD calculation
        exp1 = close_series.ewm(span=fast, adjust=False).mean()
        exp2 = close_series.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        
        logger.debug(f"MACD calculated: {macd.iloc[-1]:.3f}, Signal: {macd_signal.iloc[-1]:.3f}")
        return macd, macd_signal
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return pd.Series(index=close_series.index, dtype=float), pd.Series(index=close_series.index, dtype=float)

def calculate_bollinger_bands(close_series, period=20, std_dev=2):
    """Calculate Bollinger Bands - Your original support/resistance logic enhanced"""
    try:
        # Your Bollinger Bands calculation
        sma = close_series.rolling(window=period).mean()
        std = close_series.rolling(window=period).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        logger.debug(f"BB calculated: Upper={upper_band.iloc[-1]:.2f}, Lower={lower_band.iloc[-1]:.2f}")
        return upper_band, sma, lower_band
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return pd.Series(index=close_series.index, dtype=float), pd.Series(index=close_series.index, dtype=float), pd.Series(index=close_series.index, dtype=float)

# ======= YOUR ORIGINAL MOVING AVERAGES (Enhanced) =======

def calculate_mas(df):
    """Your original moving averages with enhanced error handling"""
    try:
        df['ma9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['high'].rolling(200).mean()  # Your original 200 WMA based on High
        
        logger.debug("Moving averages calculated successfully")
        return df
    except Exception as e:
        logger.error(f"Error calculating moving averages: {e}")
        return df
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Calculate moving averages on RSI as shown in your charts
    df['rsi_ma9'] = df['rsi'].rolling(9).mean()
    df['rsi_ma14'] = df['rsi'].rolling(14).mean()
    df['rsi_ma26'] = df['rsi'].rolling(26).mean()
    return df

def calculate_lr_slope(df, period=21, ai_adjustment=None, symbol=None):
    """
    Calculate Linear Regression Slope on High prices (21,H) as shown in charts
    Enhanced with AI adjustment tracking
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
    
    original_slopes = pd.Series(slopes, index=df.index)
    
    # Apply AI adjustment if provided
    if ai_adjustment and ai_adjustment.get('enabled', False):
        from utils.ai_assistant import AIAssistant
        ai = AIAssistant()
        
        sensitivity_factor = ai_adjustment.get('sensitivity_factor', 1.0)
        adjustment_reason = ai_adjustment.get('reason', 'Momentum sensitivity optimization')
        
        if sensitivity_factor != 1.0:
            adjusted_slopes = original_slopes * sensitivity_factor
            
            # Log the AI modification
            if not pd.isna(original_slopes.iloc[-1]) and not pd.isna(adjusted_slopes.iloc[-1]):
                ai.log_indicator_modification(
                    indicator_name=f'LR_Slope({period})',
                    old_value=float(original_slopes.iloc[-1]),
                    new_value=float(adjusted_slopes.iloc[-1]),
                    reason=adjustment_reason,
                    symbol=symbol
                )
                
                logger.info(f"AI adjusted LR Slope({period}) for {symbol}: {original_slopes.iloc[-1]:.6f} -> {adjusted_slopes.iloc[-1]:.6f} (Sensitivity: {sensitivity_factor})")
            
            df['lr_slope'] = adjusted_slopes
        else:
            df['lr_slope'] = original_slopes
    else:
        df['lr_slope'] = original_slopes
    
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
