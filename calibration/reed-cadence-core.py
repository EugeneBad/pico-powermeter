from machine import Pin
import time

# Configuration for exercise bike
REED_PIN = 9
DEBOUNCE_TIME = 50
MIN_PULSE_INTERVAL = 100
PULSES_PER_REVOLUTION = 1
TIMEOUT_MS = 3000
AVG_SAMPLES = 3  # Average last 3 pulses for stability

# Initialize variables
reed_switch = Pin(REED_PIN, Pin.IN, Pin.PULL_UP)
pulse_times = []
debounce_time = 0
current_rpm = 0.0
last_display_rpm = -1

def reed_callback(pin):
    global debounce_time
    
    current_time = time.ticks_ms()
    
    # Check debounce and minimum interval
    if (time.ticks_diff(current_time, debounce_time) > DEBOUNCE_TIME and 
        (not pulse_times or time.ticks_diff(current_time, pulse_times[-1]) > MIN_PULSE_INTERVAL)):
        
        # Only register when switch is closed
        if pin.value() == 0:
            pulse_times.append(current_time)
            debounce_time = current_time
            
            # Keep only recent samples
            if len(pulse_times) > AVG_SAMPLES + 2:  # Keep a few extra for averaging
                pulse_times.pop(0)

# Set up interrupt
reed_switch.irq(trigger=Pin.IRQ_FALLING, handler=reed_callback)

print("Exercise Bike RPM Monitor with Averaging")
print("========================================")
print("Practical RPM range: 0-120 RPM")
print("Press Ctrl+C to stop")
print("")

try:
    while True:
        current_time = time.ticks_ms()
        
        # Check for timeout (clear old pulses)
        if pulse_times and time.ticks_diff(current_time, pulse_times[-1]) > TIMEOUT_MS:
            pulse_times = []
            new_rpm = 0.0
        elif len(pulse_times) >= 2:
            # Calculate average of last few pulses
            recent_times = pulse_times[-min(len(pulse_times), AVG_SAMPLES+1):]
            periods = []
            
            for i in range(1, len(recent_times)):
                period = recent_times[i] - recent_times[i-1]
                if period >= 500:  # Minimum 500ms = 120 RPM max (practical)
                    periods.append(period)
            
            if periods:
                avg_period = sum(periods) / len(periods)
                new_rpm = 60000 / avg_period

            else:
                new_rpm = current_rpm
        else:
            new_rpm = 0.0
        
        # Update current RPM with smoothing
        if current_rpm == 0:
            current_rpm = new_rpm
        else:
            current_rpm = 0.8 * new_rpm + 0.2 * current_rpm
        
        # Display with practical formatting
        if (abs(current_rpm - last_display_rpm) > 0.5 or 
            (current_rpm == 0 and last_display_rpm != 0)):
            
            print(f"RPM: {current_rpm:5.1f}")
            last_display_rpm = current_rpm
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("")
    print("Monitoring stopped")