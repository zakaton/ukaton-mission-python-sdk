import asyncio
from bleak import BleakScanner


async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d.name)
    deviceName = "missionDevice"
    bleDevice = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == deviceName)
    print("found?", bleDevice)

asyncio.run(main())
