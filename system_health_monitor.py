import os
import time
import logging
import threading
import psutil
from typing import Optional, Callable

# Configurable parameters (can also be set via environment variables)
CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 60))  # seconds
CPU_THRESHOLD = float(os.getenv("HEALTH_CPU_THRESHOLD", 90.0))
MEM_THRESHOLD = float(os.getenv("HEALTH_MEM_THRESHOLD", 90.0))

def setup_logger(log_level=logging.INFO) -> None:
    """Setup logging format and level."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )

def send_alert(message: str) -> None:
    """Send alert (stub for integration with email, Telegram, etc.)."""
    logging.warning(f"ALERT: {message}")
    # TODO: Integrate with notification system, e.g., Telegram, email, etc.

def monitor_system_health(
    check_interval: int = CHECK_INTERVAL,
    cpu_threshold: float = CPU_THRESHOLD,
    mem_threshold: float = MEM_THRESHOLD,
    alert_func: Optional[Callable[[str], None]] = None,
    stop_event: Optional[threading.Event] = None
) -> None:
    """
    Periodically logs CPU and memory usage, sends alerts on threshold breaches.
    Can be gracefully stopped via a threading.Event.
    """
    if alert_func is None:
        alert_func = send_alert

    logging.info(
        f"System Health Monitor started (interval={check_interval}s, "
        f"CPU threshold={cpu_threshold}%, Memory threshold={mem_threshold}%)"
    )
    while not (stop_event and stop_event.is_set()):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        logging.info(f"System Health - CPU Usage: {cpu:.1f}%, Memory Usage: {mem:.1f}%")
        if cpu > cpu_threshold:
            alert_func(f"High CPU usage detected! ({cpu:.1f}%)")
        if mem > mem_threshold:
            alert_func(f"High memory usage detected! ({mem:.1f}%)")
        # Wait, but check stop_event every second for responsive shutdown
        for _ in range(check_interval):
            if stop_event and stop_event.is_set():
                break
            time.sleep(1)
    logging.info("System Health Monitor stopped gracefully.")

def start_system_health_monitor(
    check_interval: int = CHECK_INTERVAL,
    cpu_threshold: float = CPU_THRESHOLD,
    mem_threshold: float = MEM_THRESHOLD,
    alert_func: Optional[Callable[[str], None]] = None
) -> threading.Thread:
    """
    Starts system health monitoring in a background thread.
    Returns the thread object for management.
    """
    stop_event = threading.Event()
    thread = threading.Thread(
        target=monitor_system_health,
        args=(check_interval, cpu_threshold, mem_threshold, alert_func, stop_event),
        daemon=True
    )
    thread.stop_event = stop_event  # Attach for external control
    thread.start()
    return thread

# Example usage
if __name__ == "__main__":
    setup_logger()
    monitor_thread = start_system_health_monitor()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Shutting down system health monitor...")
        monitor_thread.stop_event.set()
        monitor_thread.join()
        logging.info("Monitor exited cleanly.")