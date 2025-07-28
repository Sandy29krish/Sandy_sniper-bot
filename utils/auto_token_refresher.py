import os
import time
import traceback
import threading
from dotenv import load_dotenv
from utils.zerodha_auth import perform_auto_login

# Load env variables
load_dotenv()

TOKEN_PATH = "/root/.kite_token_env"

def ensure_token_directory():
    token_dir = os.path.dirname(TOKEN_PATH)
    if not os.path.exists(token_dir):
        try:
            os.makedirs(token_dir, exist_ok=True)
            print(f"✅ Created token directory: {token_dir}")
        except Exception as e:
            print(f"❌ Failed to create token directory: {e}")
            return False
    return True

def read_token_from_file():
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "r") as f:
                content = f.read().strip()
                if content.startswith("KITE_ACCESS_TOKEN="):
                    return content.split("=", 1)[1]
                return content if content else None
    except Exception as e:
        print(f"❌ Error reading token file: {e}")
    return None

def save_token_to_file(access_token):
    if not access_token:
        print("❌ Cannot save empty token.")
        return False
    try:
        with open(TOKEN_PATH, "w") as f:
            f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
        print(f"✅ Access token saved to {TOKEN_PATH}")
        return True
    except Exception as e:
        print(f"❌ Failed to save token: {e}")
        return False

def refresh_token_loop(stop_event=None):
    print("🔁 Token refresher loop started.")

    if not ensure_token_directory():
        print("❌ Token directory missing and can't be created.")
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
                print("✅ Token refreshed and stored.")
                for _ in range(900):  # 15 minutes
                    if stop_event and stop_event.is_set():
                        return
                    time.sleep(1)
            else:
                print("❌ Failed to fetch token. Retrying in 60s.")
                for _ in range(60):
                    if stop_event and stop_event.is_set():
                        return
                    time.sleep(1)

        except Exception as e:
            print(f"❌ Error in token loop: {e}")
            traceback.print_exc()
            for _ in range(60):
                if stop_event and stop_event.is_set():
                    return
                time.sleep(1)

def start_token_refresher():
    stop_event = threading.Event()
    thread = threading.Thread(
        target=refresh_token_loop,
        args=(stop_event,),
        daemon=True,
        name="TokenRefresher"
    )
    thread.start()
    return thread, stop_event

if __name__ == "__main__":
    refresh_token_loop()
