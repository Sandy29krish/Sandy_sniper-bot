import os
import time
import pyotp
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from kiteconnect import KiteConnect

def perform_auto_login():
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    user_data_dir = tempfile.mkdtemp()

    try:
        chrome_options = Options()
        # Commenting headless for debugging (use headless only after fixing)
        # chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--window-size=1280,800")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://kite.zerodha.com")

        time.sleep(2)
        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(2)
        totp = pyotp.TOTP(totp_secret).now()
        driver.find_element(By.XPATH, "//input[@type='text']").send_keys(totp)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Wait for redirect
        time.sleep(5)
        current_url = driver.current_url

        if "request_token=" not in current_url:
            raise Exception("Failed to get request token. Login likely failed.")

        request_token = current_url.split("request_token=")[1].split("&")[0]

        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # Save token for reuse
        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)

        print(f"[✅] Access Token Generated: {access_token}")
        driver.quit()
        return access_token

    except Exception as e:
        print("❌ Error during login:", str(e))
        driver.quit()
        raise e
    finally:
        shutil.rmtree(user_data_dir, ignore_errors=True)
