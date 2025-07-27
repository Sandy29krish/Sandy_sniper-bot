import os
import time
import traceback
import threading
from utils.zerodha_auth import perform_auto_login

TOKEN_PATH = "/root/.kite_token_env"

def refresh_token_loop(stop_event=None):
    """Main token refresh loop that can be stopped via stop_event"""
    print("✅ Token refresher loop started.")
    while True:
        if stop_event and stop_event.is_set():
            print("🛑 Token refresher stopped.")
            break
            
        try:
            access_token = perform_auto_login()
            if access_token:
                os.environ["KITE_ACCESS_TOKEN"] = access_token

                with open(TOKEN_PATH, "w") as f:
                    f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
                print(f"✅ Access token refreshed and saved at {TOKEN_PATH}")
                
                # Sleep for 15 minutes on successful refresh
                for _ in range(900):  # 15 minutes = 900 seconds
                    if stop_event and stop_event.is_set():
                        return
                    time.sleep(1)
            else:
                print("❌ Failed to get access token, retrying in 1 minute...")
                for _ in range(60):  # 1 minute
                    if stop_event and stop_event.is_set():
                        return
                    time.sleep(1)
                    
        except Exception as e:
            print("❌ Error refreshing token:", e)
            traceback.print_exc()
            # Wait 1 minute before retry on error
            for _ in range(60):
                if stop_event and stop_event.is_set():
                    return
                time.sleep(1)

def start_token_refresher():
    """Start token refresher in a separate thread and return thread and stop event"""
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
