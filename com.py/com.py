from micropython import const
import asyncio
import aioble
from bluetooth import UUID
import struct
from machine import Pin
from random import randint

nom = "ESP32-Power"  # Device name

# UUIDs for BLE communication
CPS_SERVICE_UUID = 			UUID( 0x1818 )  # UUID for the Cycling Power Service
CPS_MEASUREMENT_CHAR_UUID = UUID( 0x2A63 )  # UUID for power measurement
CPS_FEATURE_CHAR_UUID = 	UUID( 0x2A65 )  # UUID for CPS feature characteristic
SENSOR_LOCATION_UUID = 		UUID( 0x2A5D )  # UUID for sensor location
DEVICE_NAME_UUID = 			UUID( 0x2A00 )  # UUID for the Device Name
APPEARANCE_UUID = 			UUID( 0x2A01 )  # UUID for Appearance
BATTERY_SERVICE_UUID = 		UUID( 0x180F )  # UUID for Battery Service
BATTERY_LEVEL_CHAR_UUID = 	UUID( 0x2A19 )  # UUID for Battery Level
DEVICE_INFORMATION_UUID = 	UUID( 0x180A )  # UUID for device information
MANUFACTURER_NAME_UUID = 	UUID( 0x2A29 )  # UUID for manufacturer name
MODEL_NUMBER_UUID = 		UUID( 0x2A29 )  # UUID for model number
FIRMWARE_VERSION_UUID = 	UUID( 0x2A26 )  # UUID for firmware version

# Flags for data
FLAGS_INSTANTANEOUS_POWER = 0x02  # Indicates instantaneous power measurement

# Cycling Power
power_service = aioble.Service(CPS_SERVICE_UUID)
# Cathegories
power_characteristic = aioble.Characteristic			(power_service, CPS_MEASUREMENT_CHAR_UUID, read = True, notify = True, capture = True)
cps_feature_characteristic = aioble.Characteristic		(power_service, CPS_FEATURE_CHAR_UUID, read = True) #write = True
device_name_characteristic = aioble.Characteristic		(power_service, DEVICE_NAME_UUID, read = True, )
appearance_characteristic = aioble.Characteristic		(power_service, APPEARANCE_UUID, read = True)
sensor_location_characteristic = aioble.Characteristic	(power_service, SENSOR_LOCATION_UUID, read = True)

# Battery Service
battery_service = aioble.Service(BATTERY_SERVICE_UUID)
# Cathegorie
battery_level_characteristic = aioble.Characteristic(battery_service, BATTERY_LEVEL_CHAR_UUID, read = True, notify = True)

# Device Information :
device_information = aioble.Service(DEVICE_INFORMATION_UUID)
# Cathegories
manufacturer_name_characteristic = aioble.Characteristic(device_information, MANUFACTURER_NAME_UUID, read = True)
model_number_characteristic = aioble.Characteristic		(device_information, MODEL_NUMBER_UUID, read = True)
firmware_version_characteristic = aioble.Characteristic	(device_information, FIRMWARE_VERSION_UUID, read = True)


# Simulates reading power data
def get_power_data():
    # Generate a random power value between 100W and 400W
    power = randint(100, 400)
    # Data structure: [Flags (2 bytes), Instantaneous Power (2 bytes)]
    return struct.pack("<Hh", FLAGS_INSTANTANEOUS_POWER, power)

# Task to periodically update power data
def power_data_task():
    a=2  # Placeholder (function implementation is incomplete)
    try:
        power_data = get_power_data()
        # Write data to the characteristic
        #power_characteristic.notify(power_data)
        power_characteristic.write(power_data, send_update = True)
        power = struct.unpack("<Hh", power_data)[1]  # Extract power for display
        print(f"Power sent: {power} W : {power_data}")
    except Exception as e:
            print(f"Error updating power data: {e}")

# Main function to set up the BLE device
async def main():
    print("Initializing BLE device...")

    # Register services and characteristics
    # notification = True
    
    aioble.register_services(power_service, battery_service, device_information)

    print("Starting BLE advertising...")
    # Values for Cycling Power
    sensor_location_characteristic.write(struct.pack("<B", 0x03)) # Hub (location)
    cps_feature_characteristic.write(struct.pack("<H", 0x0004000C)) # Example bitmask for CPS capabilities
    device_name_characteristic.write(nom.encode('utf-8'))
    appearance_characteristic.write(struct.pack("<H", 0x0484)) # Cycling Power Sensor
    # Value for Battery Service
    battery_level_characteristic.write(struct.pack("<B", 50))
    # Values for Device Information
    manufacturer_name_characteristic.write(b"Max_Industries")
    model_number_characteristic.write(b"v1_is_the_best")
    firmware_version_characteristic.write(b"Firmware 1.6.9")
    
    # Start BLE advertising
    print("Waiting for connection...")
    connection = await aioble.advertise(250_000, name = nom, services = [CPS_SERVICE_UUID, BATTERY_SERVICE_UUID, DEVICE_INFORMATION_UUID],)
    
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

