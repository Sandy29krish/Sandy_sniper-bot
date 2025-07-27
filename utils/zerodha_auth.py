import os
import pyotp
import time
from kiteconnect import KiteConnect

def perform_auto_login():
    print("[🔁] Starting Zerodha auto-login...")

    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    # Print debug info
    print(f"[ENV] API_KEY: {api_key}")
    print(f"[ENV] API_SECRET: {api_secret}")
    print(f"[ENV] USER_ID: {user_id}")
    print(f"[ENV] PASSWORD: {password}")
    print(f"[ENV] TOTP_SECRET: {totp_secret}")

    if not all([api_key, api_secret, user_id, password, totp_secret]):
        raise ValueError("❌ One or more environment variables are not set. Check .bashrc or .env file.")

    try:
        # Generate TOTP
        totp = pyotp.TOTP(totp_secret)
        totp_code = totp.now()
        print(f"[✅] TOTP generated: {totp_code}")

        # Selenium login
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://kite.zerodha.com/")

        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(1)

        driver.find_element(By.ID, "pin").send_keys(totp_code)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)

        current_url = driver.current_url
        print(f"[🔗] Redirected URL: {current_url}")

        request_token = None
        if "request_token=" in current_url:
            request_token = current_url.split("request_token=")[-1].split("&")[0]
            print(f"[✅] Request Token: {request_token}")
        else:
            raise Exception("❌ Request token not found after login.")

        driver.quit()

        # Generate session
        kite = KiteConnect(api_key=api_key)
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session_data["access_token"]

        # Save access token
        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)

        print(f"[🔐] Access token saved: {access_token}")
        return access_token

    except Exception as e:
        print(f"[❌] Auto login failed: {e}")
        return None
