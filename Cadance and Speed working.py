from micropython import const
import asyncio
import aioble
from bluetooth import UUID, BLE
import struct
from random import randint
import time

nom = "ESP32Cadence"  # Device name

# UUIDs for BLE communication
CSC_SERVICE_UUID = 			UUID( 0x1816 )  # UUID for the Cycling Speed and cadence
CSC_MEASUREMENT_CHAR_UUID = UUID( 0x2A5B )  # UUID measurement
CSC_FEATURE_CHAR_UUID = 	UUID( 0x2A5C )  # UUID feature characteristic

wheel_revolution = 0x01
crank_revolution = 0x02
cumulative_wheel_revolutions = 0x03
cumulative_crank_revolutions = 0x04

flags = crank_revolution # To add put "|"

cadence_service = aioble.Service(CSC_SERVICE_UUID)
# Cathegories
csc_measurement_characteristic = aioble.Characteristic			(cadence_service, CSC_MEASUREMENT_CHAR_UUID, notify = True) 
ccs_feature_characteristic = aioble.Characteristic				(cadence_service, CSC_FEATURE_CHAR_UUID, read = True)

wheel_revolution = total_wheel_revolution = current_time = total_crank_revolution = 0
# Simulates reading data
def get_cadence():
    global total_wheel_revolution, last_wheel_event_time, current_time
    
    current_time = int(time.ticks_ms() /1000 * 1024) & 0xFFFF
    last_wheel_event_time = current_time
    
    wheel_revolution = randint(1, 4)
    total_wheel_revolution += wheel_revolution
    
    return struct.pack("<BHH", flags, total_wheel_revolution, last_wheel_event_time)

def cadence_data_task():
    global total_wheel_revolution, wheel_revolution, total_crank_revolution

    # Write data to the characteristic
    cadence_data = get_cadence()
    csc_measurement_characteristic.write(cadence_data, send_update = True)
    print(cadence_data)
    print(f"Packed Data (hex): {cadence_data.hex()}")
    wheel_revolution_data = struct.unpack("<BHH", cadence_data)[1] 
    last_wheel_event_time_data = struct.unpack("<BHH", cadence_data)[2]
    print(f'revolution total {wheel_revolution_data} : time {last_wheel_event_time_data}')

# Main function to set up the BLE device
async def main():
    global wheel_revolution, total_wheel_revolution, current_time, total_crank_revolution

    print("Initializing BLE device...")
    print("Starting BLE advertising...")
    
    ccs_feature_characteristic.write(struct.pack('<H', flags))
    aioble.register_services(cadence_service)
    
    # Start BLE advertising
    print("Waiting for connection...")
    connection = await aioble.advertise(500_000, name = nom, services = [CSC_SERVICE_UUID], appearance = 0x0482) #appearance = 0x0482 # BATTERY_SERVICE_UUID, DEVICE_INFORMATION_UUID
    print("Connected to", connection.device)
 
    a = 1
    while connection.is_connected() and a == 1:
        cadence_data_task()
        await asyncio.sleep(1)
    
    print('disconnected')
    a = 0
    await asyncio.sleep(3)
    asyncio.run(main())

# Execute the main loop
asyncio.run(main())

