import requests
import logging

class Notifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_telegram(self, text: str) -> bool:
        """
        Send a Telegram message using the provided token and chat ID.
        """
        if not self.token or not self.chat_id:
            logging.error("Telegram token or chat ID missing.")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
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
