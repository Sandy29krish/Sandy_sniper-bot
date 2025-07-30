import os
import time
import threading
from utils.zerodha_auth import perform_auto_login

stop_event = threading.Event()

def token_refresh_loop():
    print("🔄 Token refresher loop started.")
    while not stop_event.is_set():
        try:
            perform_auto_login()
            print("✅ Token refreshed. Sleeping for 15 minutes...")
        except Exception as e:
            print("❌ Failed to fetch token. Retrying in 60s.")
            time.sleep(60)
            continue
        time.sleep(900)  # Refresh every 15 minutes

def start_token_refresher():
    refresher_thread = threading.Thread(target=token_refresh_loop, daemon=True)
    refresher_thread.start()
    return refresher_thread

if __name__ == "__main__":
    try:
        start_token_refresher()
        while not stop_event.is_set():
            time.sleep(5)
    except KeyboardInterrupt:
        print("⛔ Stopping token refresher.")
        stop_event.set()
