from machine import Pin
import time

REED_PIN = 9

reed_switch = Pin(REED_PIN, Pin.IN, Pin.PULL_UP)
last_pulse_time = time.ticks_ms()
smoothed_rpm = 0
last_display_rpm = -1
SMOOTHING_FACTOR = 0.3  # Lower = more smoothing (0.1-0.5)

print("Exponential Smoothing RPM Monitor")
print("=================================")

try:
    last_state = reed_switch.value()
    
    while True:
        current_time = time.ticks_ms()
        current_state = reed_switch.value()
        time_since_last_pulse = time.ticks_diff(current_time, last_pulse_time)
        
        # Edge detection
        if last_state == 1 and current_state == 0:
            if reed_switch.value() == 0:
                if time_since_last_pulse > 25:
                    last_pulse_time = current_time
                    
                    if time_since_last_pulse > 0:
                        raw_rpm = 60000 / time_since_last_pulse
                        
                        if 10 <= raw_rpm <= 2000:
                            # Exponential smoothing
                            if smoothed_rpm == 0:
                                smoothed_rpm = raw_rpm
                            else:
                                smoothed_rpm = (SMOOTHING_FACTOR * raw_rpm) + ((1 - SMOOTHING_FACTOR) * smoothed_rpm)
        
        last_state = current_state
        
        # Reset to zero
        if time_since_last_pulse > 1200:
            smoothed_rpm = 0
        
        # Display with change detection
        if abs(smoothed_rpm - last_display_rpm) > 1 or (smoothed_rpm == 0 and last_display_rpm != 0):
            print(f"RPM: {smoothed_rpm:6.1f}")
            last_display_rpm = smoothed_rpm
        
        time.sleep(0.002)
        
except KeyboardInterrupt:
    print("Stopped")