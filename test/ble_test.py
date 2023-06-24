import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d.name)
    bleDevice = await BleakScanner.find_device_by_name("missionDevice")
    print("found?", bleDevice)

asyncio.run(main())