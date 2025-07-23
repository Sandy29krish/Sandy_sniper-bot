import time
from datetime import datetime
import pytz
from sniper_swing_trade import SniperSwingBot
from utils.telegram_bot import send_telegram_message
from utils.telegram_commands import start_telegram_command_server, get_swing_bot_status
from utils.auto_token_refresher import refresh_access_token_if_needed

# Telegram server is started in main.py

IST = pytz.timezone('Asia/Kolkata')

TRADING_START_HOUR = 8
TRADING_END_HOUR = 16
TRADING_END_MINUTE = 30

bot_active = False
startup_alert_sent = False
shutdown_alert_sent = False
swing_bot = SniperSwingBot()

def is_market_hours():
    now = datetime.now(IST)
    start = now.replace(hour=TRADING_START_HOUR, minute=0, second=0, microsecond=0)
    end = now.replace(hour=TRADING_END_HOUR, minute=TRADING_END_MINUTE, second=0, microsecond=0)
    return now.weekday() < 5 and start <= now <= end

def run_swing_strategy():
    global bot_active, startup_alert_sent, shutdown_alert_sent
    
    send_telegram_message("🟢 Sniper Swing Runner Started")
    
    while True:
        now = datetime.now(IST)

        if is_market_hours() and get_swing_bot_status():
            if not bot_active:
                if not startup_alert_sent:
                    send_telegram_message("🟢 Sniper Swing Bot Started - Market Hours Active")
                    startup_alert_sent = True
                    shutdown_alert_sent = False
                bot_active = True

            try:
                # Refresh token if needed
                token = refresh_access_token_if_needed()
                if not token:
                    send_telegram_message("⚠️ Failed to refresh access token")
                    time.sleep(30)
                    continue
                    
                swing_bot.run()
            except Exception as e:
                send_telegram_message(f"⚠️ Error running bot: {e}")
        else:
            if bot_active:
                swing_bot.force_exit_all()
                if not shutdown_alert_sent:
                    send_telegram_message("🔴 Market Closed - Sniper Swing Bot Stopped. All positions exited.")
                    shutdown_alert_sent = True
                    startup_alert_sent = False
                bot_active = False

        time.sleep(60)

if __name__ == "__main__":
    run_swing_strategy()