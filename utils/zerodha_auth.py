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

    # ✅ Create a dedicated temp dir for Chrome user data
    user_data_dir = tempfile.mkdtemp()
    driver = None  # ✅ Prevent UnboundLocalError

    try:
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        # ✅ Start Chrome browser
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://kite.zerodha.com/")

        time.sleep(2)
        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(2)
        otp = pyotp.TOTP(totp_secret).now()
        driver.find_element(By.XPATH, "//input[@type='text']").send_keys(otp)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(3)
        current_url = driver.current_url
        if "request_token=" not in current_url:
            raise Exception("Login failed: Request token not found.")

        # ✅ Extract request token
        request_token = current_url.split("request_token=")[1].split("&")[0]

        # ✅ Generate access token
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        return access_token

    except Exception as e:
        print(f"[AutoLogin Error] {e}")
        return None

    finally:
        # ✅ Safe cleanup
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"[Cleanup Warning] Failed to close driver: {e}")
        try:
            shutil.rmtree(user_data_dir)
        except Exception as e:
            print(f"[Cleanup Warning] Failed to delete temp folder: {e}")
