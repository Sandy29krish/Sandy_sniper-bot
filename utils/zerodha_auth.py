import os
import time
import logging
import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from kiteconnect import KiteConnect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def perform_auto_login():
    try:
        # Load credentials
        user_id = os.getenv("KITE_USER_ID")
        password = os.getenv("KITE_PASSWORD")
        totp_secret = os.getenv("KITE_TOTP_SECRET")
        api_key = os.getenv("KITE_API_KEY")
        api_secret = os.getenv("KITE_API_SECRET")

        # Validate env vars
        missing = []
        for var, val in {
            "KITE_USER_ID": user_id,
            "KITE_PASSWORD": password,
            "KITE_TOTP_SECRET": totp_secret,
            "KITE_API_KEY": api_key,
            "KITE_API_SECRET": api_secret
        }.items():
            if not val:
                missing.append(var)

        if missing:
            raise Exception(f"❌ Missing environment variables: {', '.join(missing)}")

        # Generate TOTP
        totp = pyotp.TOTP(totp_secret).now()
        logger.info(f"✅ TOTP Generated: {totp}")

        # Chrome headless config
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)

        logger.info("🌐 Opening Kite login page...")
        driver.get("https://kite.zerodha.com/")
        time.sleep(2)

        # Fill login form
        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)

        # Enter TOTP
        driver.find_element(By.TAG_NAME, "input").send_keys(totp)
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(3)

        # Debug: Print final URL
        current_url = driver.current_url
        logger.info(f"🔎 Final redirected URL: {current_url}")

        if "request_token=" not in current_url:
            driver.quit()
            raise Exception("❌ Login succeeded but request token not found in URL.")

        request_token = current_url.split("request_token=")[1].split("&")[0]
        driver.quit()

        logger.info("🔐 Request token obtained, generating access token...")

        kite = KiteConnect(api_key=api_key)
        session = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session["access_token"]

        # Save token
        with open("/root/.kite_token_env", "w") as f:
            f.write(f"KITE_ACCESS_TOKEN={access_token}\n")

        os.environ["KITE_ACCESS_TOKEN"] = access_token
        logger.info("✅ Access token saved and set.")

        return access_token

    except Exception as e:
        logger.error(f"❌ Auto login failed: {e}")
        return None
