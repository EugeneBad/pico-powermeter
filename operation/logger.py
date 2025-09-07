import time

# --- Logging function ---
def log(level, message):
    """Simple logger that prints messages with a timestamp."""
    ms_since_boot = time.ticks_ms()
    print(f"[{ms_since_boot}] [{level}] {message}")