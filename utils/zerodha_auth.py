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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Navigating to Kite login page...")
        driver.get("https://kite.zerodha.com")

        wait = WebDriverWait(driver, 30)  # Increased timeout

        # Step 1: Wait for page to load and enter user ID and password
        print("🔍 Waiting for login form to load...")
        user_elem = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        pass_elem = wait.until(EC.presence_of_element_located((By.ID, "password")))
        
        print("📝 Entering credentials...")
        user_elem.clear()
        user_elem.send_keys(user_id)
        pass_elem.clear()
        pass_elem.send_keys(password)
        
        # Wait for submit button to be clickable
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
        submit_btn.click()
        
        print("✅ Credentials submitted, waiting for TOTP page...")
        time.sleep(3)  # Give page time to load

        # Step 2: Enter TOTP with better element detection
        totp = pyotp.TOTP(totp_secret).now()
        print(f"🔐 Generated TOTP: {totp}")
        
        # Try multiple selectors for TOTP input
        totp_input = None
        totp_selectors = [
            '//input[@type="text"]',
            '//input[@placeholder="Enter PIN"]',
            '//input[contains(@class, "pin")]',
            '//input[@id="pin"]',
            '//input[@name="pin"]'
        ]
        
        for selector in totp_selectors:
            try:
                totp_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                print(f"✅ Found TOTP input using selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not totp_input:
            raise NoSuchElementException("Failed to locate TOTP input field")
        
        totp_input.clear()
        totp_input.send_keys(totp)
        
        # Wait for TOTP submit button
        totp_submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
        totp_submit_btn.click()
        
        print("✅ TOTP submitted, waiting for redirect...")
        time.sleep(5)  # Give more time for redirect

        # Step 3: Extract request_token from URL with better handling
        current_url = driver.current_url
        print("🔍 Current URL after login:", current_url)

        # Wait for URL to contain request_token
        max_attempts = 10
        for attempt in range(max_attempts):
            current_url = driver.current_url
            print(f"🔄 Attempt {attempt + 1}: Checking URL for request_token...")
            
            if "request_token=" in current_url:
                break
            elif "error" in current_url.lower():
                raise Exception("❌ Login failed - error detected in URL")
            elif attempt < max_attempts - 1:
                time.sleep(2)
                driver.refresh()  # Try refreshing if token not found
            else:
                raise Exception("❌ Request token not found in URL after multiple attempts. Login failed.")

        request_token = current_url.split("request_token=")[-1].split("&")[0]
        print(f"✅ Request token extracted: {request_token}")

        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # ✅ Save access token
        kite.set_access_token(access_token)
        print("✅ Access Token generated successfully")

        return access_token

    except NoSuchElementException as e:
        print(f"❌ NoSuchElementException during auto-login: {e}")
        print("💡 This usually means the page elements didn't load properly or selectors are outdated")
        return None
    except TimeoutException as e:
        print(f"❌ TimeoutException during auto-login: {e}")
        print("💡 Page took too long to load or elements weren't found")
        return None
    except Exception as e:
        print(f"❌ Error during auto-login: {e}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
                print("🧹 Browser driver closed successfully")
            except Exception as e:
                print(f"⚠️ Warning: Error closing driver: {e}")
        
        try:
            shutil.rmtree(user_data_dir, ignore_errors=True)
            print("🧹 Temporary user data directory cleaned up")
        except Exception as e:
            print(f"⚠️ Warning: Error cleaning up temp directory: {e}")
