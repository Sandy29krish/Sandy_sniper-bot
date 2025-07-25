import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")


class Notifier:
    @staticmethod
    def send(message: str):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ID:
            print("❌ Telegram credentials not set.")
            return

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_ID,
            "text": message
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code != 200:
                print(f"❌ Failed to send Telegram message: {response.text}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")
