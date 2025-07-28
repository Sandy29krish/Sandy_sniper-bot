import os
import time
import pyotp
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from kiteconnect import KiteConnect

def perform_auto_login():
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    user_data_dir = tempfile.mkdtemp()
    driver = None

    try:
        # ✅ Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 900)
        driver.get("https://kite.zerodha.com")

        wait = WebDriverWait(driver, 20)

        # ✅ Login steps
        wait.until(EC.presence_of_element_located((By.ID, "userid"))).send_keys(user_id)
        wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).click()

        time.sleep(1)  # brief pause
        totp = pyotp.TOTP(totp_secret).now()
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))).send_keys(totp)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).click()

        time.sleep(3)  # wait for redirect
        current_url = driver.current_url
        if "request_token=" not in current_url:
            raise Exception("Login failed or TOTP not accepted.")

        request_token = current_url.split("request_token=")[-1].split("&")[0]

        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # ✅ Save token for reuse
        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)

        return access_token

    except Exception as e:
        print("❌ Error during auto-login:", e)
        return None

    finally:
        if driver:
            driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)
