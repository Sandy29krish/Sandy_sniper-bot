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

def safe_send_keys(driver, by, value, text):
    for _ in range(3):
        try:
            elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
            elem.clear()
            elem.send_keys(text)
            return
        except Exception:
            driver.refresh()
    raise Exception(f"Failed to locate and send keys to {value}")

def safe_click(driver, by, value):
    for _ in range(3):
        try:
            elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
            elem.click()
            return
        except Exception:
            driver.refresh()
    raise Exception(f"Failed to click {value}")

def perform_auto_login():
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    user_id = os.getenv("KITE_USER_ID")
    password = os.getenv("KITE_PASSWORD")
    totp_secret = os.getenv("KITE_TOTP_SECRET")

    if not all([api_key, api_secret, user_id, password, totp_secret]):
        raise Exception("❌ Missing environment variables")

    # Setup headless Chrome
    user_data_dir = tempfile.mkdtemp()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://kite.zerodha.com")

        # Step 1: Login with credentials
        safe_send_keys(driver, By.ID, "userid", user_id)
        safe_send_keys(driver, By.ID, "password", password)
        safe_click(driver, By.XPATH, '//button[@type="submit"]')

        # Step 2: TOTP
        totp = pyotp.TOTP(totp_secret).now()
        safe_send_keys(driver, By.TAG_NAME, "input", totp)
        safe_click(driver, By.XPATH, '//button[@type="submit"]')

        # Step 3: Wait for request_token
        WebDriverWait(driver, 15).until(EC.url_contains("request_token="))
        current_url = driver.current_url
        request_token = current_url.split("request_token=")[1].split("&")[0]

        # Step 4: Generate session
        kite = KiteConnect(api_key=api_key)
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session_data["access_token"]

        # Step 5: Save token for reuse
        with open("/root/.kite_token_env", "w") as f:
            f.write(access_token)

        print("✅ Token generated and saved successfully!")
        return access_token

    except Exception as e:
        print("❌ Auto-login failed:", str(e))
        raise

    finally:
        try:
            driver.quit()
        except:
            pass
        shutil.rmtree(user_data_dir, ignore_errors=True)

# Manual test trigger
if __name__ == "__main__":
    perform_auto_login()
