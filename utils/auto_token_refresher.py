import os
import time
import traceback
from utils.zerodha_auth import perform_auto_login

TOKEN_PATH = "/root/.kite_token_env"

def refresh_token_loop():
    print("✅ Token refresher loop started.")
    while True:
        try:
            access_token = perform_auto_login()
            os.environ["KITE_ACCESS_TOKEN"] = access_token

            with open(TOKEN_PATH, "w") as f:
                f.write(f"KITE_ACCESS_TOKEN={access_token}\n")
            print(f"✅ Access token refreshed and saved at {TOKEN_PATH}")

            time.sleep(60 * 15)  # refresh every 15 minutes
        except Exception as e:
            print("❌ Error refreshing token:", e)
            traceback.print_exc()
            time.sleep(60)  # wait and retry

if __name__ == "__main__":
    refresh_token_loop()
