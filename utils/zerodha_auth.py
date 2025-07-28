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
        # Load credentials from environment
        user_id = os.getenv("KITE_USER_ID")
        password = os.getenv("KITE_PASSWORD")
        totp_secret = os.getenv("KITE_TOTP_SECRET")
        api_key = os.getenv("KITE_API_KEY")
        api_secret = os.getenv("KITE_API_SECRET")

        # Validate all required environment variables
        missing_vars = []
        if not user_id:
            missing_vars.append("KITE_USER_ID")
        if not password:
            missing_vars.append("KITE_PASSWORD")
        if not totp_secret:
            missing_vars.append("KITE_TOTP_SECRET")
        if not api_key:
            missing_vars.append("KITE_API_KEY")
        if not api_secret:
            missing_vars.append("KITE_API_SECRET")
            
        if missing_vars:
            raise Exception(f"❌ Missing required environment variables: {', '.join(missing_vars)}")

        # Generate TOTP
        totp = pyotp.TOTP(totp_secret).now()
        logger.info(f"✅ Generated TOTP: {totp}")

        # Selenium Headless Chrome Setup
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
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
            driver.quit()
            raise Exception("❌ Login failed or request token not found in redirect URL.")

        request_token = current_url.split("request_token=")[1].split("&")[0]
        driver.quit()

        logger.info("🔑 Request token obtained. Generating access token...")
        kite = KiteConnect(api_key=api_key)
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session_data["access_token"]

        if not access_token:
            raise Exception("❌ Failed to generate access token - received None")

        # Ensure the directory exists for the token file
        token_dir = os.path.dirname("/root/.kite_token_env")
        if not os.path.exists(token_dir):
            os.makedirs(token_dir, exist_ok=True)

        # Save access token to file with proper format
        try:
            with open("/root/.kite_token_env", "w") as f:
                f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
            logger.info(f"🔐 Access token saved to file: {access_token[:20]}...")
        except Exception as e:
            logger.error(f"❌ Failed to save token to file: {e}")
            # Continue even if file write fails, return the token

        # Also set in current environment
        os.environ["KITE_ACCESS_TOKEN"] = access_token
        logger.info("✅ Access token set in environment")

        return access_token

    except Exception as e:
        logger.error(f"❌ Auto login failed: {e}")
        return None
