import math
import config

def get_flat_speed(power_watts):
    """
    Calculates cycling speed on a flat road with no wind.

    Args:
        power_watts (float): The rider's power output in watts.

    Returns:
        float: The calculated speed in kilometers per hour (kph).
    """
    if power_watts <= 0:
        return 0.0
    # --- Constants and Assumptions ---
    g = 9.81      # Gravity in m/s^2
    rho = 1.225   # Air density in kg/m^3 (at sea level, 15°C)
    Crr = 0.0032   # Coefficient of Rolling Resistance for 35mm road tires on asphalt
    CdA = 0.40    # Aerodynamic Drag Area (m^2) for hands on hoods position
    eff = 0.975   # Drivetrain efficiency
    total_weight_kg = config.SYSTEM_WEIGHT_KG

    # --- Calculation ---
    power_available = power_watts * eff

    # --- Why we have to iterate ---
    # The relationship between power and speed is a "chicken-and-egg" problem.
    # 1. The force of air resistance depends on your speed (specifically, speed squared).
    # 2. The speed you can hold depends on the force of air resistance.
    #
    # This creates a cubic equation (ax^3 + bx + c = 0) where 'x' is the speed.
    # Since there's no simple, direct formula to solve this, we use a numerical
    # method. This loop is a "guess and check" approach: it starts with a guess
    # for speed, sees how much power that would require, and then makes a new,
    # smarter guess. After a few loops, the guess becomes extremely accurate.
    
    v = 5.0  # Initial guess for speed in m/s (18 kph)
    
    # Loop 5 times to refine the speed calculation
    for _ in range(5):
        F_gravity = g * total_weight_kg
        F_rolling = F_gravity * Crr
        F_aero = 0.5 * CdA * rho * (v ** 2)
        
        power_required = (F_rolling + F_aero) * v
        
        # Adjust the speed using a simplified numerical solver
        v = v * (power_available / power_required + 2) / 3

    # Convert final speed from meters/second to kilometers/hour
    return v * 3.6
    
print(get_flat_speed(160))