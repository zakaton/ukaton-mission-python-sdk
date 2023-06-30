from UkatonMissionSDK.base import BaseUkatonMission, BaseUkatonMissions
from bleak import BleakScanner, BleakClient, BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from typing import Optional
from UkatonMissionSDK.enumerations import *

import logging

logging.basicConfig()
logger = logging.getLogger("BLEUkatonMission")
logger.setLevel(logging.DEBUG)


class BLEUkatonMission(BaseUkatonMission):
    @staticmethod
    def generate_uuid(value):
        return f"5691eddf-{value}-4420-b7a5-bb8751ab5181"

    SENSOR_DATA_CONFIGURATION_CHARACTERISTIC_UUID: str = generate_uuid("6001")
    SENSOR_DATA_CHARACTERISTIC_UUID: str = generate_uuid("6002")

    def __init__(self):
        super().__init__()
        self.device: Optional[BLEDevice] = None
        self.client: Optional[BleakClient] = None

    async def connect(self, device_name: str):
        self.device_name: str = device_name
        logger.debug(f'looking for "{self.device_name}"...')
        self.device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == self.device_name)
        if self.device is None:
            logger.debug("couldn't find device")
            return
        logger.debug("found device!")
        logger.debug("connecting to device...")
        async with BleakClient(self.device, self._disconnection_handler) as client:
            logger.debug("connected to device!")
            self.client = client

            logger.debug("starting notifications...")
            await client.start_notify(self.__class__.SENSOR_DATA_CHARACTERISTIC_UUID, self.sensor_data_notification_handler)
            logger.debug("started notifications!")

            self._connection_handler()

    def sensor_data_notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        logger.debug(f"received sensor data: {data}")
        self.parse_sensor_data(data)

    async def disconnect(self):
        if self.is_connected:
            pass

    async def _send_sensor_data_configuration(self, serialized_sensor_data_configuration: bytearray):
        if self.is_connected:
            await self.client.write_gatt_char(self.__class__.SENSOR_DATA_CONFIGURATION_CHARACTERISTIC_UUID, serialized_sensor_data_configuration)

    async def _send_vibration(self, message: bytearray):
        if self.is_connected:
            pass


class BLEUkatonMissions(BaseUkatonMissions):
    pass
