from machine import Pin
import time
import config


_DEBOUNCE_TIME = 50
_MIN_PULSE_INTERVAL = 100
_AVG_SAMPLES = 3  # Average last 3 pulses for stability

class CadenceSensor:
    def __init__(self):
        self.pulse_times = []
        self.debounce_time = 0
        self.reed_switch = Pin(config.REED_PIN, Pin.IN, Pin.PULL_UP)
        self.current_rpm = 0.0
        self.last_display_rpm = -1

        # Set up interrupt
        self.reed_switch.irq(trigger=Pin.IRQ_FALLING, handler=self.reed_callback)

    def reed_callback(self, pin):
        current_time = time.ticks_ms()
        
        # Check debounce and minimum interval
        if (time.ticks_diff(current_time, self.debounce_time) > _DEBOUNCE_TIME and 
            (not self.pulse_times or time.ticks_diff(current_time, self.pulse_times[-1]) > _MIN_PULSE_INTERVAL)):
            
            # Only register when switch is closed
            if pin.value() == 0:
                self.pulse_times.append(current_time)
                self.debounce_time = current_time
                
                # Keep only recent samples
                if len(self.pulse_times) > _AVG_SAMPLES + 2:  # Keep a few extra for averaging
                    self.pulse_times.pop(0)
    
    def calculate_cadence(self, current_time):
  
        # Check for timeout (clear old pulses)
        if self.pulse_times and time.ticks_diff(current_time, self.pulse_times[-1]) > config.TIMEOUT_MS:
            self.pulse_times = []
            new_rpm = 0.0
        elif len(self.pulse_times) >= 2:
            # Calculate average of last few pulses
            recent_times = self.pulse_times[-min(len(self.pulse_times), _AVG_SAMPLES+1):]
            periods = []
            
            for i in range(1, len(recent_times)):
                period = recent_times[i] - recent_times[i-1]
                if period >= 1000 * 60/config.MAX_RPM:  # Minimum 500ms = 120 RPM max (practical)
                    periods.append(period)
            
            if periods:
                avg_period = sum(periods) / len(periods)
                new_rpm = 60000 / avg_period

            else:
                new_rpm = self.current_rpm
        else:
            new_rpm = 0.0
        
        # Update current RPM with smoothing
        if self.current_rpm == 0:
            self.current_rpm = new_rpm
        else:
            self.current_rpm = 0.8 * new_rpm + 0.2 * self.current_rpm
        
        # if (abs(self.current_rpm - self.last_display_rpm) > 0.5 or 
        #     (self.current_rpm == 0 and self.last_display_rpm != 0)):
        self.last_display_rpm = self.current_rpm
        return self.current_rpm