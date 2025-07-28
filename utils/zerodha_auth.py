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

# -------------------------- SAFE HELPERS ----------------------------
def safe_send_keys(driver, by, value, text):
    for _ in range(5):
        try:
            elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
            elem.clear()
            elem.send_keys(text)
            return
        except Exception:
            time.sleep(1)
    raise Exception(f"Failed to send keys to {value}")

def safe_click(driver, by, value):
    for _ in range(5):
        try:
            elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
            time.sleep(0.5)
            elem.click()
            return
        except Exception:
            time.sleep(2)
            driver.refresh()
    raise Exception(f"Failed to click {value}")

# -------------------------- MAIN LOGIN FUNCTION ----------------------------
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

    driver = webdriver.Chrome(options=chrome_options)

    try:
        kite = KiteConnect(api_key=api_key)
        login_url = kite.login_url()
        driver.get(login_url)

        # Login Step 1 - User ID and Password
        safe_send_keys(driver, By.ID, "userid", user_id)
        safe_send_keys(driver, By.ID, "password", password)
        safe_click(driver, By.XPATH, '//button[@type="submit"]')

        # Login Step 2 - TOTP
        totp = pyotp.TOTP(totp_secret).now()
        safe_send_keys(driver, By.ID, "totp", totp)
        safe_click(driver, By.XPATH, '//button[@type="submit"]')

        # Get Request Token
        WebDriverWait(driver, 10).until(lambda d: "request_token" in d.current_url)
        request_token = driver.current_url.split("request_token=")[1].split("&")[0]

        # Generate Access Token
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        with open("/root/.kite_token_env", "w") as f:
            f.write(f"KITE_ACCESS_TOKEN={access_token}\n")

        print("\n✅ Token generated and saved successfully!")
        return access_token

    except Exception as e:
        print(f"\n❌ Auto-login failed: {e}")
        raise
    finally:
        driver.quit()
        shutil.rmtree(user_data_dir)

# -------------------------- MAIN ----------------------------
if __name__ == "__main__":
    perform_auto_login()
