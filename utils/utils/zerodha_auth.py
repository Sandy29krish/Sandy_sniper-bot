import os
from kiteconnect import KiteConnect

def get_kite_instance():
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")

    if not api_key or not access_token:
        raise Exception("Missing KITE_API_KEY or KITE_ACCESS_TOKEN in environment variables.")

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite
