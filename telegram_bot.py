import os
import requests
import logging

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(text: str) -> bool:
    """
    Send a message to a Telegram chat.

    Returns True if sent successfully, False otherwise.
    Logs errors instead of printing.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram token or chat ID not set in environment variables.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error("Failed to send Telegram message: %s", response.text)
            return False
        return True
    except Exception as e:
        logging.exception(f"Error sending telegram message: {e}")
        return False