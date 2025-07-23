import requests

BOT_TOKEN = "8143962740:AAHHPGho9tckm3E9Hgv9n8sfBsmAn2CinPs"
CHAT_ID = "7797661300"
MESSAGE = "✅ Telegram Bot Test message from Sniper Bot"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": MESSAGE}

response = requests.post(url, data=payload)
print("Telegram message sent:", response.status_code == 200)
print("Response:", response.json())
