import os
import time
import pyotp
import logging
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.INFO)

def perform_auto_login():
    logging.info("[AUTO LOGIN] Starting Zerodha login process")

    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    # Debug print
    print(f"[DEBUG] USER ID = {user_id}")
    print(f"[DEBUG] PASSWORD = {password}")
    print(f"[DEBUG] TOTP = {pyotp.TOTP(totp_secret).now()}")

    user_data_dir = tempfile.mkdtemp()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://kite.zerodha.com")
        time.sleep(2)

        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)

        otp = pyotp.TOTP(totp_secret).now()
        driver.find_element(By.XPATH, "//input[@type='text']").send_keys(otp)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(4)

        current_url = driver.current_url
        print(f"[DEBUG] Current URL after login: {current_url}")

        if "request_token=" not in current_url:
            raise Exception("Login failed or request_token not found")

        request_token = current_url.split("request_token=")[1].split("&")[0]
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        print(f"[✅] Access token received: {access_token}")
        return access_token

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

    finally:
        driver.quit()
        shutil.rmtree(user_data_dir)

def refresh_token_loop():
    while True:
        token = perform_auto_login()
        if token:
            os.environ["KITE_ACCESS_TOKEN"] = token
            with open("/root/.kite_token_env", "w") as f:
                f.write(f"KITE_ACCESS_TOKEN={token}\n")
            print("[✅] Token refreshed and saved to /root/.kite_token_env")
        else:
            print("❌ Failed to get access token, retrying in 1 minute...")
        time.sleep(60)

if __name__ == "__main__":
    refresh_token_loop()
