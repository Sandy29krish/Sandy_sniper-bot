import threading
from core.sniper_swing import SniperSwing
from utils.swing_config import SWING_CONFIG
from utils.telegram_commands import start_telegram_command_server
from utils.auto_token_refresher import start_token_refresher
from utils.system_health_monitor import start_system_health_monitor

def run_swing_bot():
    bot = SniperSwing(capital=170000, config=SWING_CONFIG)
    while True:
        bot.run()

if __name__ == "__main__":
    # Start token refresher
    start_token_refresher()

    # Start system health monitor
    start_system_health_monitor()

    # Start Telegram command server in separate thread
    telegram_thread = threading.Thread(target=start_telegram_command_server, daemon=True)
    telegram_thread.start()

    # Start swing bot in main thread
    run_swing_bot()
