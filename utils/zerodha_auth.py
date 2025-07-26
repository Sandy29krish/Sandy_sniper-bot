import pyotp
import requests
import os
from kiteconnect import KiteConnect

def perform_auto_login():
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    # Generate TOTP
    totp = pyotp.TOTP(totp_secret).now()

    session = requests.Session()

    # Step 1: Initiate login
    login_url = "https://kite.zerodha.com/api/login"
    data = {
        "user_id": user_id,
        "password": password,
        "twofa_value": totp,
        "twofa_type": "totp"
    }
    resp = session.post(login_url, data=data)
    if not resp.ok or "request_id" not in resp.json().get("data", {}):
        raise Exception(f"Login failed: {resp.text}")

    request_id = resp.json()["data"]["request_id"]

    # Step 2: Get request token from request_id
    token_url = f"https://kite.zerodha.com/api/login/token"
    token_resp = session.post(token_url, data={"request_id": request_id})
    if not token_resp.ok or "data" not in token_resp.json():
        raise Exception(f"Token fetch failed: {token_resp.text}")

    access_token = token_resp.json()["data"]["access_token"]

    # Step 3: Return access_token
    return access_token
