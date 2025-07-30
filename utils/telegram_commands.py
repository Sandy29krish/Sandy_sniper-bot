import os
import requests
import logging

# Fetch token and chat ID from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

def send_telegram_message(message: str):
    """
    Send a message to your Telegram chat using the bot token.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_ID,
        "text": message,
        "parse_mode": "Markdown"  # optional: format message as Markdown
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

def check_telegram_health():
    """
    Check if the Telegram bot API is reachable and healthy.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("ok", False)
        return False
    except Exception as e:
        logging.error(f"Telegram health check failed: {e}")
        return False
