import os
import pyotp
from kiteconnect import KiteConnect

def perform_auto_login():
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    if not totp_secret:
        raise ValueError("❌ KITE_TOTP_SECRET not found. Check your .bashrc or environment settings.")

    # Generate TOTP
    totp = pyotp.TOTP(totp_secret)
    totp_code = totp.now()

    kite = KiteConnect(api_key=api_key)

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        import time

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://kite.zerodha.com/")

        # Enter credentials
        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(1)
        driver.find_element(By.ID, "pin").send_keys(totp_code)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(5)
        request_token = None
        current_url = driver.current_url
        if "request_token=" in current_url:
            request_token = current_url.split("request_token=")[-1].split("&")[0]

        driver.quit()

        if not request_token:
            raise Exception("Request token not found")

        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # Write to token file
        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)

        print("[✅] Access token updated:", access_token)
        return access_token

    except Exception as e:
        print("[❌] Error during auto login:", str(e))
        return None
