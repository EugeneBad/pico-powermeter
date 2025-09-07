import struct
import bluetooth
from logger import log

# --- BLE Service and Characteristic UUIDs ---
_CPS_SERVICE_UUID = bluetooth.UUID(0x1818)
_CPS_MEASUREMENT_CHAR_UUID = bluetooth.UUID(0x2A63)
_CSCS_SERVICE_UUID = bluetooth.UUID(0x1816)
_CSCS_MEASUREMENT_CHAR_UUID = bluetooth.UUID(0x2A5B)
_CSCS_FEATURE_CHAR_UUID = bluetooth.UUID(0x2A5C)

# --- Advertising Details ---
_ADV_APPEARANCE_CYCLING_POWER = const(1156)

# --- BLE Peripheral Class ---
class BLEPeripheral:
    def __init__(self, name):
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)
        
        # Define services and characteristics
        power_char = (_CPS_MEASUREMENT_CHAR_UUID, bluetooth.FLAG_NOTIFY,)
        power_service = (_CPS_SERVICE_UUID, (power_char,),)
        csc_char = (_CSCS_MEASUREMENT_CHAR_UUID, bluetooth.FLAG_NOTIFY,)
        csc_feature_char = (_CSCS_FEATURE_CHAR_UUID, bluetooth.FLAG_READ,) # Feature is read-only

        csc_service = (_CSCS_SERVICE_UUID, (csc_char,csc_feature_char),)

        # Register services and store handles
        services = (power_service, csc_service)
        ((self.power_handle,), (self.csc_handle,self.csc_feature_handle),) = self.ble.gatts_register_services(services)
        
        # Set the value of the CSC Feature characteristic
        # Value 0x0003 indicates both Wheel and Crank Revolution Data are supported
        self.ble.gatts_write(self.csc_feature_handle, struct.pack("<H", 0x0003))
        
        self.conn_handle = None
        self.advertising = False
        
        # Start advertising
        self._advertise()

    def _irq(self, event, data):
        """BLE event handler"""
        if event == 1: # _IRQ_CENTRAL_CONNECT
            self.conn_handle, _, _ = data
            log("INFO", f"Connected to central device: handle={self.conn_handle}")
            self.ble.gap_advertise(0) # Stop advertising on connect
            self.advertising = False
        elif event == 2: # _IRQ_CENTRAL_DISCONNECT
            self.conn_handle = None
            log("INFO", "Disconnected from central device")
            self._advertise() # Start advertising again

    def _advertise(self):
        """Constructs and starts the BLE advertising payload."""
        payload = bytearray()
        
        def _add_payload(adv_type, data):
            nonlocal payload
            payload += struct.pack("BB", len(data) + 1, adv_type) + data
        
        # --- FIX: Use the raw integer UUIDs for advertising ---
        # The struct.pack function needs a number, not a bluetooth.UUID object.
        _add_payload(0x03, struct.pack("<H", 0x1818)) # Cycling Power Service
        _add_payload(0x03, struct.pack("<H", 0x1816)) # Cycling Speed and Cadence
        
        _add_payload(0x19, struct.pack("<h", _ADV_APPEARANCE_CYCLING_POWER))
        _add_payload(0x09, self.name.encode())

        self.ble.gap_advertise(100000, payload)
        self.advertising = True
        log("INFO", f"Advertising as '{self.name}'...")
        
    def is_connected(self):
        return self.conn_handle is not None

    def send_power(self, power_watts):
        if not self.is_connected(): return
        flags = 0x00
        power_data = struct.pack("<Hh", flags, power_watts)
        self.ble.gatts_notify(self.conn_handle, self.power_handle, power_data)

    # def send_csc_data(self, cumulative_crank_revs, last_crank_event_time, cumulative_wheel_revs, last_wheel_event_time):
    #     if not self.is_connected(): return
        
    #     # Flags for both Wheel and Crank Revolution Data
    #     flags = 0x03
    #     log("DEBUG", f"Sending CSC data: Flags={flags}, Wheel Revs={cumulative_wheel_revs}, Wheel Time={last_wheel_event_time}, Crank Revs={cumulative_crank_revs}, Crank Time={last_crank_event_time}")

    #     # Pack the data according to the BLE CSCS specification
    #     # <B: Flags, <H: Cumulative Wheel Revs, <H: Last Wheel Event Time, <H: Cumulative Crank Revs, <H: Last Crank Event Time
    #     csc_data = struct.pack("<BHH", flags, cumulative_wheel_revs, last_wheel_event_time, cumulative_crank_revs, last_crank_event_time)
        
    #     self.ble.gatts_notify(self.conn_handle, self.csc_handle, csc_data)

    ### CSC Flags: https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/CSCS_v1.0/out/en/index-en.html#UUID-13a6d96c-b74e-a2ec-8f05-3ab21f119c35
    def send_speed(self, cumulative_wheel_revs,  cumulative_wheel_time):
        if not self.is_connected(): return
        
        flags = 0x01 # Flag for Speed data only

        speed_data = struct.pack("<BIH", flags, cumulative_wheel_revs,  cumulative_wheel_time)
        self.ble.gatts_notify(self.conn_handle, self.csc_handle, speed_data)

    def send_cadence(self, cumulative_crank_revs, cumulative_crank_time):
        if not self.is_connected(): return
        
        flags = 0x02 # Flag for Cadence data only
        
        cadence_data = struct.pack("<BHH", flags, cumulative_crank_revs, cumulative_crank_time)
        self.ble.gatts_notify(self.conn_handle, self.csc_handle, cadence_data)