import random

# --- Data Simulation Configuration ---
MIN_POWER = 180
MAX_POWER = 200

def get_power():
    return random.randint(MIN_POWER, MAX_POWER)