import machine
import time
import config

# --- Setup ---
# Set up the ADC on GPIO pin 27.


class KConstant:
    def __init__(self):
        self.pot = machine.ADC(config.POTENTIOMETER_PIN)

    def get_k_constant(self):
        """
        Performs linear interpolation to find the k constant for a given voltage.
        Returns:
            float: The interpolated k constant value.
        """
        raw_adc_value = self.pot.read_u16()
        voltage = (raw_adc_value / config.MAX_ADC_VALUE) * config.PICO_REFERENCE_VOLTAGE
        voltage_data = config.LEVEL_VOLTAGE_SORTED
        k_constant_data = config.LEVEL_K_SORTED

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