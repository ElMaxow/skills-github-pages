from micropython import const
import asyncio
import aioble
from bluetooth import UUID, BLE
import struct

name = "MaxPower"  # Device name

# UUIDs for BLE communication
CPS_SERVICE_UUID =			UUID( 0x1818 )  # UUID for the Cycling Power Service
CPS_MEASUREMENT_CHAR_UUID =	UUID( 0x2A63 )  # UUID for power measurement
CPS_FEATURE_CHAR_UUID = 	UUID( 0x2A65 )  # UUID for CPS feature characteristic
SENSOR_LOCATION_UUID =		UUID( 0x2A5D )  # UUID for sensor location
CONTROL_PONINT_UUID =		UUID( 0x2A66 )  # UUID for Cycling Power Control Point

BATTERY_SERVICE_UUID =		UUID( 0x180F )  # UUID for Battery Service
BATTERY_LEVEL_CHAR_UUID =	UUID( 0x2A19 )  # UUID for Battery Level

DEVICE_INFORMATION_UUID =	UUID( 0x180A )  # UUID for device information
MANUFACTURER_NAME_UUID =	UUID( 0x2A29 )  # UUID for manufacturer name
MODEL_NUMBER_UUID =			UUID( 0x2A24 )  # UUID for model number
FIRMWARE_VERSION_UUID =		UUID( 0x2A26 )  # UUID for firmware version
SERIAL_NUMER_UUID =			UUID( 0x2A25 )  # UUID for serial number
# Flags for data
INSTANTANEOUS_POWER =			0x00
CRANK_REVOLUTION_DATA_PRESENT =	0x10

flags = INSTANTANEOUS_POWER # To add put "|"
feature_flag = const( 0x0C	) # Value of CPS_FEATURE_CHAR
  
# Cycling Power
power_service = aioble.Service(CPS_SERVICE_UUID)
# Categories
power_characteristic = aioble.Characteristic			(power_service, CPS_MEASUREMENT_CHAR_UUID, notify = True) 
cps_feature_characteristic = aioble.Characteristic		(power_service, CPS_FEATURE_CHAR_UUID, read = True)
sensor_location_characteristic = aioble.Characteristic	(power_service, SENSOR_LOCATION_UUID, read = True)
control_point_characteristic = aioble.Characteristic	(power_service, CONTROL_PONINT_UUID, write = True, indicate = True)

# Battery Service
battery_service = aioble.Service(BATTERY_SERVICE_UUID)
# Categories
battery_level_characteristic = aioble.Characteristic(battery_service, BATTERY_LEVEL_CHAR_UUID, read = True, notify = True)

# Device Information :
device_information = aioble.Service(DEVICE_INFORMATION_UUID)
# Categories
manufacturer_name_characteristic = aioble.Characteristic(device_information, MANUFACTURER_NAME_UUID, read = True)
model_number_characteristic = aioble.Characteristic		(device_information, MODEL_NUMBER_UUID, read = True)
firmware_version_characteristic = aioble.Characteristic	(device_information, FIRMWARE_VERSION_UUID, read = True)
serial_number_characteristic = aioble.Characteristic	(device_information, SERIAL_NUMER_UUID, read = True)

# Task to periodically update power data
def power_data_task(power):
    try:
        print(f"Power sent: {power} W")
        bit_power = struct.pack("<Hh", flags, power)
        power_characteristic.write(bit_power, send_update = True)
    except Exception as e:
            print(f"Error updating power data: {e}")

# Main function to set up the BLE device
async def main(power = 0):
    print("Initializing BLE device...")
    print("Starting BLE advertising...")
    print("Waiting for connection...")
    
    # Start BLE advertising
    aioble.register_services(power_service, battery_service, device_information)
    connection = await aioble.advertise(250_000, name = name, services = [CPS_SERVICE_UUID], appearance = 0x0484) # BATTERY_SERVICE_UUID, DEVICE_INFORMATION_UUID
    
    # Values for Cycling Power
    sensor_location_characteristic.write(struct.pack	("<B", 0x0C)) # Hub (location)
    cps_feature_characteristic.write(struct.pack		("<i", feature_flag)) # Basic power measurement only
    # Value for Battery Service
    battery_level_characteristic.write(struct.pack		("<B", 50))
    # Values for Device Information
    manufacturer_name_characteristic.write				(b"Max_Industries")
    model_number_characteristic.write					(b"v1_is_the_best")
    firmware_version_characteristic.write				(b"Firmware 1.6.9")
    serial_number_characteristic.write					(b"00000001")
    
    print("Connected to", connection.device)

    while connection.is_connected():
        power_data_task(power)
        data = control_point_characteristic.read()
        print(data)
        await asyncio.sleep(1)
    
    print('disconnected')
    await asyncio.sleep(3)
    asyncio.run(main())

# Execute the main loop
asyncio.run(main(power = 200))



