import os
import time
import logging
import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def perform_auto_login():
    try:
        # Load credentials from environment
        user_id = os.getenv("KITE_USER_ID")
        password = os.getenv("KITE_PASSWORD")
        totp_secret = os.getenv("KITE_TOTP_SECRET")
        api_key = os.getenv("KITE_API_KEY")
        api_secret = os.getenv("KITE_API_SECRET")

        if not all([user_id, password, totp_secret, api_key, api_secret]):
            raise Exception("❌ Missing one or more required environment variables.")

        # Generate TOTP
        totp = pyotp.TOTP(totp_secret).now()

        # Selenium Headless Chrome Setup
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        logger.info("🌐 Opening Kite login page...")
        driver.get("https://kite.zerodha.com/")

        time.sleep(2)
        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(2)
        driver.find_element(By.TAG_NAME, "input").send_keys(totp)
        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(3)
        current_url = driver.current_url
        if "request_token=" not in current_url:
            raise Exception("❌ Login failed or request token not found in redirect URL.")

        request_token = current_url.split("request_token=")[1].split("&")[0]
        driver.quit()

        logger.info("🔑 Request token obtained. Generating access token...")
        kite = KiteConnect(api_key=api_key)
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session_data["access_token"]

        # Save access token to file
        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)
        logger.info(f"🔐 Access token saved: {access_token}")

        return access_token

    except Exception as e:
        logger.error(f"❌ Auto login failed: {e}")
        return None
