from flask import Flask, request
import threading
from utils.telegram_bot import send_telegram_message
from sniper_swing import SniperSwing
from utils.swing_config import SWING_CONFIG

app = Flask(__name__)
bot = SniperSwing(capital=170000, config=SWING_CONFIG)

bot_thread = None
bot_running = False

def run_bot():
    global bot_running
    bot_running = True
    while bot_running:
        bot.run()

@app.route('/start_swing', methods=['GET'])
def start_swing():
    global bot_thread
    if bot_thread and bot_thread.is_alive():
        return "Bot already running."
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    send_telegram_message("✅ Sniper Swing Bot started.")
    return "Started Swing Bot."

@app.route('/stop_swing', methods=['GET'])
def stop_swing():
    global bot_running
    bot_running = False
    send_telegram_message("⏹️ Sniper Swing Bot stopped.")
    return "Stopped Swing Bot."

@app.route('/status', methods=['GET'])
def status():
    status = "Running" if bot_running else "Stopped"
    return f"Sniper Swing Bot status: {status}"

def start_telegram_command_server():
    app.run(host='0.0.0.0', port=5000)
