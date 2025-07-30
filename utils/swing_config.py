SWING_CONFIG = {
    'NIFTY': {
        'instrument_token': 256265,
        'exchange': 'NSE',
        'lot_size': 75,
        'trend': 'uptrend',
        'full_name': 'NIFTY 50 Index'
        # Note: CPR levels are now calculated dynamically based on timeframes
        # See utils/cpr_calculator.py for dynamic CPR calculation
    },
    'BANKNIFTY': {
        'instrument_token': 260105,
        'exchange': 'NSE',
        'lot_size': 30,
        'trend': 'uptrend',
        'full_name': 'Bank Nifty'
        # Note: CPR levels are now calculated dynamically based on timeframes
        # See utils/cpr_calculator.py for dynamic CPR calculation
    },
    'SENSEX': {
        'instrument_token': 11910258,
        'exchange': 'BSE',
        'lot_size': 10,
        'trend': 'uptrend',
        'full_name': 'SENSEX Index'
        # Note: CPR levels are now calculated dynamically based on timeframes
        # See utils/cpr_calculator.py for dynamic CPR calculation
    },
    'FINNIFTY': {
        'instrument_token': 257801,
        'exchange': 'NSE',
        'lot_size': 40,
        'trend': 'uptrend',
        'full_name': 'Nifty Financial Services'
        # Note: CPR levels are now calculated dynamically based on timeframes
        # See utils/cpr_calculator.py for dynamic CPR calculation
    }
}

# Total capital allocated for swing strategy
CAPITAL = 170000  # You can adjust this as needed

# List of symbols extracted from SWING_CONFIG keys
SYMBOLS = list(SWING_CONFIG.keys())

# Indian Market Trading Hours (IST)
MARKET_HOURS = {
    'pre_market_start': '09:00',
    'market_open': '09:15',
    'market_close': '15:30',
    'post_market_end': '15:45'
}

# Trading Session Configuration
TRADING_SESSIONS = {
    'morning_session': ('09:15', '11:30'),
    'afternoon_session': ('11:30', '15:30'),
    'friday_early_close': '15:15'
}

# Risk Management
RISK_CONFIG = {
    'max_daily_trades': 3,
    'max_simultaneous_trades': 3,
    'max_capital_per_trade': 0.33,  # 33% of capital per trade
    'swing_based_exits': True,  # User's custom swing exit strategy
    'partial_profit_on_swing_high': True,  # Take partial profits at swing highs
    'hold_remaining_for_higher_targets': True  # Hold remaining position for higher targets
}

# Dynamic CPR Configuration
CPR_CONFIG = {
    'enabled': True,
    'timeframes': ['daily', 'weekly', 'intraday'],
    'cache_duration': 300,  # 5 minutes
    'validation_enabled': True,
    'strength_threshold': 0.6  # Minimum CPR strength for trade validation
}
