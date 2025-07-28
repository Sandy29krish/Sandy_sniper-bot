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

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://kite.zerodha.com")

        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "userid"))).send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        totp = pyotp.TOTP(totp_secret).now()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "input"))).send_keys(totp)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        wait.until(EC.url_contains("request_token="))
        request_token = driver.current_url.split("request_token=")[1].split("&")[0]

        kite = KiteConnect(api_key=api_key)
        session = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session["access_token"]

        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)

        print("✅ Token fetched and stored successfully.")
        return access_token

    except Exception as e:
        print("❌ Error during auto-login:", str(e))
        raise e

    finally:
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)
