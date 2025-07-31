import os
import time
import pyotp
import tempfile
import shutil
import threading
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from kiteconnect import KiteConnect

# Global lock to prevent concurrent Chrome sessions
_chrome_lock = threading.Lock()

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
    """DISABLED - Chrome conflicts resolved"""
    print("🛡️ Auto-login DISABLED - Chrome conflicts resolved")
    raise Exception("Chrome automation disabled - use manual token generation")

def perform_auto_login_with_credentials(api_key, user_id, password, totp_secret):
    """DISABLED - Chrome conflicts resolved"""
    print("🛡️ Auto-login DISABLED - Chrome conflicts resolved")
    raise Exception("Chrome automation disabled - use manual token generation")

# -------------------------- MAIN ----------------------------
if __name__ == "__main__":
    perform_auto_login()
