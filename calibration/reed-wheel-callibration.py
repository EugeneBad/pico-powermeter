from machine import Pin
import time

REED_PIN = 9

reed_switch = Pin(REED_PIN, Pin.IN, Pin.PULL_UP)
last_pulse_time = time.ticks_ms()
smoothed_rpm = 0
SMOOTHING_FACTOR = 0.3

# Instrumentation
max_rpm_reached = 0
start_time = 0
measurement_active = False
coasting_down = False

# Multi-run configuration
TOTAL_RUNS = 5
current_run = 0
run_times = []  # Store coast-down times for each run
run_complete = False

print("Multi-Run Coast-Down Timer")
print("==========================")
print(f"Recording {TOTAL_RUNS} runs automatically")
print("Procedure per run:")
print("1. Spin up PAST 800 RPM")
print("2. RELEASE and let it coast down")
print("3. Timing starts at 750 RPM (on way down)")
print("4. Timing stops at 300 RPM")
print("")

try:
    last_state = reed_switch.value()
    last_display_rpm = -1
    
    while current_run < TOTAL_RUNS:
        current_time = time.ticks_ms()
        current_state = reed_switch.value()
        time_since_last_pulse = time.ticks_diff(current_time, last_pulse_time)
        
        # RPM measurement
        if last_state == 1 and current_state == 0:
            if reed_switch.value() == 0:
                if time_since_last_pulse > 25:
                    last_pulse_time = current_time
                    if time_since_last_pulse > 0:
                        raw_rpm = 60000 / time_since_last_pulse
                        if 10 <= raw_rpm <= 2000:
                            if smoothed_rpm == 0:
                                smoothed_rpm = raw_rpm
                            else:
                                smoothed_rpm = (SMOOTHING_FACTOR * raw_rpm) + ((1 - SMOOTHING_FACTOR) * smoothed_rpm)
        
        last_state = current_state
        
        if time_since_last_pulse > 1200:
            smoothed_rpm = 0
        
        # Track maximum RPM reached
        if smoothed_rpm > max_rpm_reached:
            max_rpm_reached = smoothed_rpm
        
        # State logic for current run
        if not measurement_active:
            if max_rpm_reached >= 800:
                if not coasting_down:
                    coasting_down = True
                    print(f"Run {current_run + 1}: ✅ Reached 800+ RPM! Release and coast down...")
                
                # Wait for RPM to drop to 750 on the way down
                if coasting_down and smoothed_rpm <= 750:
                    measurement_active = True
                    start_time = current_time
                    print(f"Run {current_run + 1}: ⏱️  TIMING STARTED! (750 RPM)")
        
        else:
            # Measurement is active
            elapsed = time.ticks_diff(current_time, start_time) / 1000.0
            
            # Target reached - complete current run
            if smoothed_rpm <= 300:
                coast_time = elapsed
                run_times.append(coast_time)
                current_run += 1
                
                print("")
                print(f"Run {current_run} COMPLETE!")
                print("=======================")
                print(f"Time: {coast_time:.2f} seconds")
                print(f"Runs completed: {current_run}/{TOTAL_RUNS}")
                print("=======================")
                
                # Reset for next run
                measurement_active = False
                coasting_down = False
                max_rpm_reached = 0
                smoothed_rpm = 0
                last_pulse_time = current_time
                
                if current_run < TOTAL_RUNS:
                    print("")
                    print(f"Ready for run {current_run + 1}...")
                    print("Spin up past 800 RPM")
                else:
                    run_complete = True
        
        # Display with state context
        if abs(smoothed_rpm - last_display_rpm) > 1:
            if coasting_down and not measurement_active:
                print(f"Run {current_run + 1}: Coasting down... {smoothed_rpm:6.1f} RPM (waiting for 750)")
            elif measurement_active:
                elapsed = time.ticks_diff(current_time, start_time) / 1000.0
                print(f"Run {current_run + 1}: Timing... {smoothed_rpm:6.1f} RPM | Time: {elapsed:5.1f}s")
            else:
                print(f"Run {current_run + 1}: Spinning up... {smoothed_rpm:6.1f} RPM")
            
            last_display_rpm = smoothed_rpm
        
        time.sleep(0.002)
    
    # All runs completed - show statistics
    if run_complete:
        print("")
        print("🎉 ALL RUNS COMPLETED!")
        print("======================")
        print("Coast-down times:")
        for i, time_val in enumerate(run_times, 1):
            print(f"Run {i}: {time_val:.2f} seconds")
        
        print("")
        print("📊 Statistics:")
        print(f"Best time:    {min(run_times):.2f} seconds")
        print(f"Worst time:   {max(run_times):.2f} seconds")
        print(f"Average time: {sum(run_times)/len(run_times):.2f} seconds")
        print(f"Total time:   {sum(run_times):.2f} seconds")
        print("======================")
        
        # Wait indefinitely after completion
        while True:
            time.sleep(1)
        
except KeyboardInterrupt:
    print("")
    if run_times:
        print("Partial results:")
        for i, time_val in enumerate(run_times, 1):
            print(f"Run {i}: {time_val:.2f}s")
    print("Measurement stopped by user")