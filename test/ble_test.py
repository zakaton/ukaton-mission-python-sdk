import asyncio
from bleak import BleakScanner, BleakClient
import logging

from bleak.backends.characteristic import BleakGATTCharacteristic

logging.basicConfig()
logger = logging.getLogger("ble test")
logger.setLevel(logging.DEBUG)


def generate_uuid(value):
    return f"5691eddf-{value}-4420-b7a5-bb8751ab5181"


def sensor_data_notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    logger.info("%s: %r", characteristic.description, data)


sensor_data_configuration_characteristic_uuid = generate_uuid("6001")
sensor_data_characteristic_uuid = generate_uuid("6002")

logger.debug(
    f"sensor_data_configuration_characteristic_uuid: {sensor_data_configuration_characteristic_uuid}")
logger.debug(
    f"sensor_data_characteristic_uuid: {sensor_data_characteristic_uuid}")


async def run(loop):
    if False:
        devices = await BleakScanner.discover()
        for d in devices:
            print(d.name)
    deviceName = "missionDevice"
    logger.debug('finding device "{}"...'.format(deviceName))
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == deviceName)
    if (device is None):
        logger.debug("didn't find device :(")
        return
    logger.debug("found device!")
    logger.debug("connecting to device...")
    async with BleakClient(device) as client:
        logger.debug("connected!")

        logger.debug("starting notifications")
        await client.start_notify(sensor_data_characteristic_uuid, sensor_data_notification_handler)
        logger.debug("enabling sensor data")
        await client.write_gatt_char(sensor_data_configuration_characteristic_uuid, bytearray([0, 3, 5, 20, 0]), True)
        logger.debug("enabled sensor data")
        # await client.stop_notify(sensor_data_characteristic_uuid)
        await asyncio.sleep(10.0, loop=loop)


loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
