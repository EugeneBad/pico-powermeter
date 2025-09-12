import math
import config

def get_power(crank_cadence, k_constant):
    flywheel_speed = config.G_RATIO * crank_cadence * (math.pi / 30) # in rad/s
    power = k_constant * flywheel_speed ** 2
    return int(power)