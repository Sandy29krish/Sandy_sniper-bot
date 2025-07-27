import os import pyotp import time import logging from kiteconnect import KiteConnect from selenium import webdriver from selenium.webdriver.chrome.options import Options from selenium.webdriver.common.by import By from selenium.webdriver.common.keys import Keys from selenium.webdriver.support.ui import WebDriverWait from selenium.webdriver.support import expected_conditions as EC

def perform_auto_login(): api_key = os.getenv("KITE_API_KEY") api_secret = os.getenv("KITE_API_SECRET") user_id = os.getenv("KITE_USER_ID") password = os.getenv("KITE_PASSWORD") totp_secret = os.getenv("KITE_TOTP_SECRET")

if not totp_secret:
    raise ValueError("❌ KITE_TOTP_SECRET not set in environment")

try:
    # Generate TOTP code
    totp = pyotp.TOTP(totp_secret)
    totp_code = totp.now()

    # Setup headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://kite.zerodha.com")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "userid"))).send_keys(user_id)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'input'))).send_keys(totp_code)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    # Wait for redirection
    time.sleep(3)
    current_url = driver.current_url
    print(f"[🔍] Current URL after login: {current_url}")

    if "request_token=" in current_url:
        request_token = current_url.split("request_token=")[-1].split("&")[0]
        print(f"[✅] Request token extracted: {request_token}")
    else:
        print("[❌] Request token NOT found in URL!")
        raise Exception("Request token not found in redirected URL.")

    driver.quit()

    kite = KiteConnect(api_key=api_key)
    session_data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = session_data["access_token"]

    # Save access token
    with open("/root/.kite_token_env", "w") as f:
        f.write(access_token)

    print(f"[🔐] Access token saved: {access_token}")
    return access_token

except Exception as e:
    print(f"❌ Auto login failed: {e}")
    return None

