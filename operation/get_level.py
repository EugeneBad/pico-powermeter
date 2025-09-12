import machine
import time

# --- Setup ---
# Set up the ADC on GPIO pin 27.
potentiometer = machine.ADC(27)

# IMPORTANT: Set this to the voltage of your battery.
# For accurate voltage readings, this should be as close to the
# actual battery voltage as possible.
REFERENCE_VOLTAGE = 1.0 

# The Pico's ADC is 16-bit, so its maximum raw value is 65535.
# This corresponds to an input of 3.3V.
MAX_ADC_VALUE = 65535
PICO_REFERENCE_VOLTAGE = 3.3
voltage_data = [0.13, 0.33, 0.44, 0.5, 0.6, 0.66, 0.7, 0.74, 0.77, 0.79, 0.81, 0.83, 0.85, 0.87, 0.88]
k_constant_data = [0.003760894314, 0.006044133342, 0.007750843403, 0.009002498, 0.01227374179, 0.01426839859, 0.01569968343, 0.0192645198, 0.02130007769, 0.02274186995, 0.02379413777, 0.0251979919, 0.02547825268, 0.02597731124, 0.02627527831]

def get_k_constant(voltage):
    """
    Performs linear interpolation to find the k constant for a given voltage.

    Args:
        voltage (float): The voltage value to interpolate.
    Returns:
        float: The interpolated k constant value.
    """

    x1 = y1 = x2 = y2 = 0.00
    
    # Check for values outside the range
    if voltage <= voltage_data[0]:
        return k_constant_data[0]
    if voltage >= voltage_data[-1]:
        return k_constant_data[-1]

    # Find the correct interval
    for i in range(len(voltage_data) - 1):
        if voltage_data[i] <= voltage <= voltage_data[i+1]:
            x1, y1 = voltage_data[i], k_constant_data[i]
            x2, y2 = voltage_data[i+1], k_constant_data[i+1]
            break

    # Perform linear interpolation
    return y1 + ((voltage - x1) * (y2 - y1) / (x2 - x1))

# --- Main Loop ---
while True:
    # Read the raw 16-bit value from the ADC.
    raw_adc_value = potentiometer.read_u16()
    
    # --- Calculations ---
    
    # 1. Calculate the voltage being read at the pin.
    # The ADC scales its 0-65535 reading relative to its own 3.3V reference.
    voltage = (raw_adc_value / MAX_ADC_VALUE) * PICO_REFERENCE_VOLTAGE
    k_constant = get_k_constant(voltage)
    
    # Print the results to the console.
    print(f"Voltage: {voltage:.2f} V | k Constant: {k_constant}")
    
    time.sleep(0.5)