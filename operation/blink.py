import uasyncio
from machine import Pin


class LEDManager:
    """A helper class to manage the onboard LED status."""
    def __init__(self):
        """Initializes the correct LED pin for Pico or Pico W."""
        self.led = Pin("LED", Pin.OUT)
        self.blink_task = None

    async def _blink_runner(self):
        """The internal coroutine that toggles the LED."""
        while True:
            self.led.toggle()
            await uasyncio.sleep_ms(500)

    def start_blinking(self):
        """Starts the LED blinking task."""
        # Cancel any previous task to ensure a clean start
        if self.blink_task:
            self.blink_task.cancel()
        self.led.off() # Ensure LED is off before starting
        self.blink_task = uasyncio.create_task(self._blink_runner())

    def set_stay_on(self):
        """Stops any blinking and sets the LED to be permanently on."""
        if self.blink_task:
            self.blink_task.cancel()
            self.blink_task = None # Clear the task reference
        self.led.on()