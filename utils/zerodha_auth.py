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

    driver = None
    user_data_dir = tempfile.mkdtemp()

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://kite.zerodha.com")
        time.sleep(2)  # Allow full page load

        wait = WebDriverWait(driver, 20)

        # Step 1: Enter user ID and password
        user_elem = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        pass_elem = wait.until(EC.presence_of_element_located((By.ID, "password")))
        user_elem.send_keys(user_id)
        pass_elem.send_keys(password)

        # Click Login (via JS to avoid click error)
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]')))
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(2)

        # Step 2: Enter TOTP
        totp = pyotp.TOTP(totp_secret).now()
        totp_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
        totp_input.send_keys(totp)

        # Click Submit (via JS)
        submit_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]')))
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(2)

        # Step 3: Extract request_token from redirected URL
        current_url = driver.current_url
        print("🔍 Current URL after login:", current_url)

        if "request_token=" not in current_url:
            raise Exception("❌ Request token not found in URL. Login failed.")

        request_token = current_url.split("request_token=")[-1].split("&")[0]

        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # ✅ Save access token to memory
        kite.set_access_token(access_token)
        print("✅ Access Token:", access_token)

        return access_token

    except Exception as e:
        print("❌ Error during auto-login:", e)
        return None

    finally:
        if driver:
            driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)
