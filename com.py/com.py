from micropython import const
import asyncio
import aioble
from bluetooth import UUID
import struct
from machine import Pin
from random import randint

# UUIDs for BLE communication
CPS_SERVICE_UUID = 			UUID(0x1818)  # UUID for the Cycling Power Service
CPS_MEASUREMENT_CHAR_UUID = UUID(0x2A63)  # UUID for power measurement
CPS_FEATURE_CHAR_UUID = 	UUID(0x2A65)  # UUID for CPS feature characteristic
SENSOR_LOCATION_UUID = 		UUID(0x2A5D)  # UUID for sensor location
DEVICE_NAME_UUID = 			UUID(0x2A00)  # UUID for the Device Name
APPEARANCE_UUID = 			UUID(0x2A01)  # UUID for Appearance

FEATURES = 0x0004000C  # Example bitmask for CPS capabilities
LOCATION = 0x03 # Hub (location)

# Appearance configuration (Cycling Power Sensor)
APPEARANCE_CYCLING_POWER_SENSOR = 0x0484

# Flags for data
FLAGS_INSTANTANEOUS_POWER = 0x02  # Indicates instantaneous power measurement

nom = "ESP32-Power"  # Device name

power_service = aioble.Service(CPS_SERVICE_UUID)
power_characteristic = aioble.Characteristic(power_service, CPS_MEASUREMENT_CHAR_UUID, read = True, notify = True, capture = True)

# Simulates reading power data
def get_power_data():
    # Generate a random power value between 100W and 400W
    power = randint(100, 400)
    # Data structure: [Flags (2 bytes), Instantaneous Power (2 bytes)]
    return struct.pack("<Hh", FLAGS_INSTANTANEOUS_POWER, power)

# Task to periodically update power data
def power_data_task():
     a=2  # Placeholder (function implementation is incomplete)

    # power_characteristic = aioble.Characteristic(power_service, bluetooth.UUID(CPS_MEASUREMENT_CHAR_UUID), read = True, notify = True, capture = True)
    # power_data = get_power_data()
    # Write data to the characteristic
    # print(power_data, "yes")
    # power_characteristic.notify(power_data)

    # power_characteristic.write(power_data, send_update=True)
    # power = struct.unpack("<Hh", power_data)[1]  # Extract power for display
    # print(f"Power sent: {power} W")

# Main function to set up the BLE device
async def main():
    print("Initializing BLE device...")

    # Register services and characteristics
    # notifiy = True
    
    sensor_location_characteristic = aioble.Characteristic(power_service, SENSOR_LOCATION_UUID, read=True)
    sensor_location_characteristic.write(struct.pack("<B", LOCATION))
    
    cps_feature_characteristic = aioble.Characteristic(power_service, CPS_FEATURE_CHAR_UUID, read=True)
    cps_feature_characteristic.write(struct.pack("<H", FEATURES))  # Example: bitmask of capabilities
    
    device_name_characteristic = aioble.Characteristic(power_service, DEVICE_NAME_UUID, read=True)
    device_name_characteristic.write(b"{nom}")

    appearance_characteristic = aioble.Characteristic(power_service, APPEARANCE_UUID, read=True)
    appearance_characteristic.write(struct.pack("<H", APPEARANCE_CYCLING_POWER_SENSOR))

    aioble.register_services(power_service)

    print("Starting BLE advertising...")

    # Start BLE advertising
    print("Waiting for connection...")
    connection = await aioble.advertise(250_000, name = nom, services = [CPS_SERVICE_UUID],)
    print("Connected to", connection.device)

    while connection.is_connected():
        power_data_task()
        await asyncio.sleep(1)
    
    print('disconnected')
    await asyncio.sleep(3)
    asyncio.run(main())

# Execute the main loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program interrupted.")
