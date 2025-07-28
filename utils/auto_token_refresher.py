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
                    return token if token else None
                else:
                    return content if content else None
    except Exception as e:
        print(f"❌ Error reading token from file: {e}")
    return None

def save_token_to_file(access_token):
    """Save token to file"""
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
    """Token refresh loop (auto retries every 15 min)"""
    print("🔄 Token refresher loop started.")

    if not ensure_token_directory():
        print("❌ Cannot continue without token directory.")
        return

    while True:
        if stop_event and stop_event.is_set():
            print("🛑 Token refresher stopped.")
            break

        try:
            access_token = perform_auto_login()
            if access_token:
                os.environ["KITE_ACCESS_TOKEN"] = access_token
                save_token_to_file(access_token)
                print("✅ Access token refreshed successfully.")

                # Sleep for 15 minutes (900 seconds)
                for _ in range(900):
                    if stop_event and stop_event.is_set():
                        return
                    time.sleep(1)

            else:
                print("❌ Access token not received. Retrying in 1 minute...")
                for _ in range(60):
                    if stop_event and stop_event.is_set():
                        return
                    time.sleep(1)

        except Exception
