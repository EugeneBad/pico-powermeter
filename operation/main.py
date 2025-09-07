import uasyncio
import time
from peripheral import BLEPeripheral
from get_cadence import get_cadence
from get_power import get_power
from get_speed import get_speed
from logger import log
from blink import LEDManager

DEVICE_NAME = "PicoPower"
WHEEL_CIRCUMFERENCE_MM = 2096 # 700-23C

async def main():
    log("INFO", "Starting BLE Sensor...")
    is_blinking = True
    led_manager = LEDManager()
    led_manager.start_blinking()

    pico_sensor = BLEPeripheral(name=DEVICE_NAME)

    # --- Cumulative values sent over BLE ---
    cumulative_crank_revs = 0
    cumulative_wheel_revs = 0
    cumulative_crank_time = 0
    cumulative_wheel_time = 0
    
    # --- Time accumulators for accurate simulation ---
    time_since_last_crank_rev_ms = 0
    time_since_last_wheel_rev_ms = 0
    
    last_processing_time_ms = time.ticks_ms()

    while True:
        if pico_sensor.is_connected():
            if is_blinking:
                led_manager.set_stay_on()
                is_blinking = False

            # --- Power Simulation ---
            power = get_power()
            pico_sensor.send_power(power)

            # --- Time Calculation ---
            current_time_ms = time.ticks_ms()
            # Use ticks_diff for safe handling of timer overflow
            elapsed_time_ms = time.ticks_diff(current_time_ms, last_processing_time_ms)
            last_processing_time_ms = current_time_ms

            # --- Crank Simulation ---
            cadence = get_cadence()
            if cadence > 0:
                time_per_crank_rev_ms = (60 / cadence) * 1000
                
                # Add the elapsed time to our accumulator
                time_since_last_crank_rev_ms += elapsed_time_ms
                
                # Use a while loop to add all revolutions that occurred during the elapsed time
                while time_since_last_crank_rev_ms >= time_per_crank_rev_ms:
                    cumulative_crank_revs += 1
                    # Update timestamp to reflect a more accurate event time
                    cumulative_crank_time += time_per_crank_rev_ms 
                    time_since_last_crank_rev_ms -= time_per_crank_rev_ms
            else:
                # Reset accumulator if cadence is zero
                time_since_last_crank_rev_ms = 0
            
            # Send cadence data on every loop to keep the client updated
            last_crank_event_time_1024 = int((cumulative_crank_time / 1000) * 1024)
            pico_sensor.send_cadence(cumulative_crank_revs, last_crank_event_time_1024)

            # --- Wheel Simulation ---
            speed_kph = get_speed()
            if speed_kph > 0:
                # Corrected formula for time per revolution in milliseconds
                time_per_wheel_rev_ms = (WHEEL_CIRCUMFERENCE_MM * 3.6) / speed_kph
                
                # Add the elapsed time to our accumulator
                time_since_last_wheel_rev_ms += elapsed_time_ms

                # Use a while loop to add all revolutions that occurred
                while time_since_last_wheel_rev_ms >= time_per_wheel_rev_ms:
                    cumulative_wheel_revs += 1
                    # Update timestamp to reflect a more accurate event time
                    cumulative_wheel_time += time_per_wheel_rev_ms
                    time_since_last_wheel_rev_ms -= time_per_wheel_rev_ms
            else:
                # Reset accumulator if speed is zero
                time_since_last_wheel_rev_ms = 0

            # Send speed data on every loop
            last_wheel_event_time_1024 = int((cumulative_wheel_time / 1000) * 1024)
            pico_sensor.send_speed(cumulative_wheel_revs, last_wheel_event_time_1024)

            log("DEBUG", f"Generated Cadence: {cadence} RPM, Speed: {speed_kph} KPH")
        else: # Not connected
            # --- Handle disconnection state change ---
            if not is_blinking:
                log("INFO", "Device disconnected, LED blinking.")
                led_manager.start_blinking()
                is_blinking = True
        # Main loop delay
        await uasyncio.sleep_ms(500)

# --- Run the main loop ---
if __name__ == "__main__":
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        print(f"[{time.ticks_ms()}] [INFO] Script stopped by user.")