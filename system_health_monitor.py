import psutil
import time
import logging
import threading

CHECK_INTERVAL = 60  # seconds

def monitor_system_health():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        logging.info(f"System Health - CPU Usage: {cpu}%, Memory Usage: {mem}%")
        if cpu > 90:
            logging.warning("High CPU usage detected!")
        if mem > 90:
            logging.warning("High memory usage detected!")
        time.sleep(CHECK_INTERVAL)

def start_system_health_monitor():
    thread = threading.Thread(target=monitor_system_health, daemon=True)
    thread.start()
