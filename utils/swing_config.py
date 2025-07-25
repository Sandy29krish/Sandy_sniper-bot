SWING_CONFIG = {
    'NIFTY': {
        'instrument_token': 256265,
        'exchange': 'NSE',
        'lot_size': 75,
        'cpr_level': 17500,
        'trend': 'uptrend',
        'full_name': 'NIFTY 50 Index'
    },
    'BANKNIFTY': {
        'instrument_token': 260105,
        'exchange': 'NSE',
        'lot_size': 30,
        'cpr_level': 42000,
        'trend': 'uptrend',
        'full_name': 'Bank Nifty'
    },
    'SENSEX': {
        'instrument_token': 11910258,
        'exchange': 'BSE',
        'lot_size': 10,
        'cpr_level': 74000,
        'trend': 'uptrend',
        'full_name': 'SENSEX Index'
    }
}

# Total capital allocated for swing strategy
CAPITAL = 170000  # You can adjust this as needed

# List of symbols extracted from SWING_CONFIG keys
SYMBOLS = list(SWING_CONFIG.keys())
