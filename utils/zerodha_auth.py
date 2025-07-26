import os
import time
import pyotp
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

    # ✅ Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={api_key}"
        driver.get(login_url)
        time.sleep(2)

        # Step 1: Enter user ID
        driver.find_element(By.ID, "userid").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)

        # Step 2: Enter TOTP
        totp = pyotp.TOTP(totp_secret).now()
        driver.find_element(By.XPATH, "//input[@type='text']").send_keys(totp)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

        # Step 3: Get request_token from URL
        current_url = driver.current_url
        if "request_token=" not in current_url:
            raise Exception("Login failed or request_token not found in URL.")
        request_token = current_url.split("request_token=")[1].split("&")[0]

        # Step 4: Generate access_token
        kite = KiteConnect(api_key=api_key)
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session_data["access_token"]
        return access_token

    finally:
        driver.quit()
