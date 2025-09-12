# The voltages are sorted and mapped to their corresponding k constant
LEVEL_VOLTAGE_SORTED = [0.13, 0.33, 0.44, 0.5, 0.6, 0.66, 0.7, 0.74, 0.77, 0.79, 0.81, 0.83, 0.85, 0.87, 0.88]
LEVEL_K_SORTED = [0.003760894314, 0.006044133342, 0.007750843403, 0.009002498, 0.01227374179, 0.01426839859, 0.01569968343, 0.0192645198, 0.02130007769, 0.02274186995, 0.02379413777, 0.0251979919, 0.02547825268, 0.02597731124, 0.02627527831]

### General settings ###
##########################
DEVICE_NAME = "PicoPowerMeter"
SYSTEM_WEIGHT_KG = 90
WHEEL_CIRCUMFERENCE_MM = 2096 # 700-23C


### Level Potentiometer settings. ###
#####################################
# The voltage across the terminals of the potentiometer when bike is on.
REFERENCE_VOLTAGE = 1.0 

# The Pico's ADC is 16-bit, so its maximum raw value is 65535.
# This corresponds to an input of 3.3V.
MAX_ADC_VALUE = 65535
PICO_REFERENCE_VOLTAGE = 3.3

POTENTIOMETER_PIN = 27
REED_SWITCH_PIN = 16

### Configuration for Reed RPM sensor ###
#########################################
REED_PIN = 9
TIMEOUT_MS = 3000
MAX_RPM = 120
# Ratio of crank revolution to flywheel revolutions
G_RATIO = 9
