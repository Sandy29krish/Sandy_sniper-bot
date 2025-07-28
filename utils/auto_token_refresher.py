import os
import time
import traceback
import threading
from dotenv import load_dotenv
from utils.zerodha_auth import perform_auto_login

# Load environment variables
load_dotenv()

TOKEN_PATH = "/root/.kite_token_env"

def ensure_token_directory():
    """Ensure the token directory exists"""
    token_dir = os.path.dirname(TOKEN_PATH)
    if not os.path.exists(token_dir):
        try:
            os.makedirs(token_dir, exist_ok=True)
            print(f"✅ Created token directory: {token_dir}")
        except Exception as e:
            print(f"❌ Failed to create token directory {token_dir}: {e}")
            return False
    return True

def read_token_from_file():
    """Read token from file if it exists"""
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "r") as f:
                content = f.read().strip()
                if content.startswith("KITE_ACCESS_TOKEN="):
                    token = content.split("=", 1)[1]
                    if token:
                        return token
                else:
                    # Handle old format (just the token)
                    return content if content else None
    except Exception as e:
        print(f"❌ Error reading token from file: {e}")
    return None

def save_token_to_file(access_token):
    """Save token to file with proper error handling"""
    if not access_token:
        print("❌ Cannot save empty token to file")
        return False

    try:
        with open(TOKEN_PATH, "w") as f:
            f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
        print(f"✅ Access token saved to {TOKEN_PATH}")
        return True
    except Exception as e:
        print(f"❌ Failed to save token to file: {e}")
        return False

def refresh_token_loop(stop_event=None):
    """Main token refresh loop that can be stopped via stop_event"""
    print("✅ Token refresher loop started.")

    if not ensure_token_directory():
        print("❌ Cannot create token directory, exiting...")
        return

    while True:
        if stop_event and stop_event.is_set():
