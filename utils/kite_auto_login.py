import pyotp
import requests
import logging
import os

KITE_USER_ID = os.getenv('KITE_USER_ID')
KITE_PASSWORD = os.getenv('KITE_PASSWORD')
TOTP_SECRET = os.getenv('TOTP_SECRET')  # Your TOTP seed for generating 2FA codes

def perform_auto_login():
    try:
        totp = pyotp.TOTP(TOTP_SECRET)
        two_fa_code = totp.now()

        # Step 1: Request login (simplified, adjust per Kite login API)
        session = requests.Session()
        login_payload = {
            "user_id": KITE_USER_ID,
            "password": KITE_PASSWORD,
            "twofa": two_fa_code
        }
        login_response = session.post("https://api.kite.trade/session/login", data=login_payload)
        login_response.raise_for_status()

        # Extract access token from response (adjust parsing as per API)
        access_token = login_response.json().get("data", {}).get("access_token")
        if not access_token:
            raise Exception("Failed to get access token from login response")

        logging.info("Kite auto login successful, access token obtained.")
        return access_token
    except Exception as e:
        logging.error(f"Error during Kite auto login: {e}")
        raise
