from machine import Pin
import bluetooth
from micropython import const
import struct
import time

# BLE UUIDs
UUID_CYCLING_POWER = const(0x1818)
UUID_POWER_MEASUREMENT = const(0x2A63)
UUID_POWER_FEATURE = const(0x2A65)
UUID_SENSOR_LOCATION = const(0x2A5D)

class BLEPowerMeter:
    def __init__(self, name="ESP32 Power Meter"):
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.connected = False
        self.led_pin = Pin(2, Pin.OUT)  # Adjust PIN number as needed

        # Register callbacks
        self.ble.irq(self.ble_irq)
        self.register_services()
        self.start_advertising()

    def register_services(self):
        # Power Service
        self.power_service = bluetooth.UUID(UUID_CYCLING_POWER)
        self.power_measurement = bluetooth.UUID(UUID_POWER_MEASUREMENT)
        self.power_feature = bluetooth.UUID(UUID_POWER_FEATURE)
        self.power_location = bluetooth.UUID(UUID_SENSOR_LOCATION)

        # Setup characteristics
        self.power_measurement_char = (
            self.power_measurement, 
            bluetooth.FLAG_NOTIFY | bluetooth.FLAG_READ
        )
        self.power_feature_char = (
            self.power_feature, 
            bluetooth.FLAG_READ
        )
        self.power_location_char = (
            self.power_location, 
            bluetooth.FLAG_READ
        )

        # Service definition
        self.services = (
            (self.power_service, (
                self.power_measurement_char,
                self.power_feature_char,
                self.power_location_char,
            )),
        )

        # Register services and extract handles
        services_handles = self.ble.gatts_register_services(self.services)
        # Extract the first service's handles
        service_handle, char_handles = services_handles[0]

        self.power_handle = service_handle
        (
            self.power_measurement_handle,
            self.power_feature_handle,
            self.power_location_handle
        ) = char_handles

        # Set initial values
        self.ble.gatts_write(self.power_feature_handle, struct.pack('<I', 0))
        self.ble.gatts_write(self.power_location_handle, bytes([5]))  # Left crank

    def start_advertising(self):
        adv_data = bytes([
            0x02, 0x01, 0x06,  # General discoverable mode
            0x03, 0x03, 0x18, 0x18,  # Complete list of 16-bit service UUIDs
            len(self.name) + 1, 0x09
        ] + list(self.name.encode('ascii')))

        self.ble.gap_advertise(interval_us=100000, adv_data=adv_data)

    def publish_power(self, instant_power, crank_revs, millis_last):
        if not self.connected:
            return False

        flags = 0b0010000000000000
        last_event_time = int((millis_last / 1000.0 * 1024.0) % 65536)

        data = struct.pack('<HHHH', flags, instant_power, crank_revs, last_event_time)
        self.ble.gatts_notify(0, self.power_measurement_handle, data)
        return True

    def ble_irq(self, event, data):
        if event == bluetooth.IRQ_CENTRAL_CONNECT:
            self.connected = True
            self.led_pin.value(1)
            print("Connected")

        elif event == bluetooth.IRQ_CENTRAL_DISCONNECT:
            self.connected = False
            self.led_pin.value(0)
            print("Disconnected")
            self.start_advertising()

        elif event == bluetooth.IRQ_GATTS_WRITE:
            conn_handle, attr_handle = data
            if attr_handle == self.power_measurement_handle + 1:  # Handle CCCD writes
                cccd_value = self.ble.gatts_read(attr_handle)
                print("CCCD Updated:", cccd_value)

# Instantiate the power meter
power_meter = BLEPowerMeter("ESP32 Power")

# Example loop to simulate power data (replace with real sensor integration)
while True:
    if power_meter.connected:
        power_meter.publish_power(instant_power=250, crank_revs=1, millis_last=int(time.ticks_ms()))
    time.sleep(1)



