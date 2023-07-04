import sys
sys.path.append(".")

from typing import Union

import logging
logging.basicConfig()
logger = logging.getLogger("graph")
logger.setLevel(logging.DEBUG)

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType

use_ble = False
device_name = "missionDevice"
device_ip_address = "192.168.1.30"
device_identifier = device_name if use_ble else device_ip_address

ukaton_mission: Union[None, BLEUkatonMission, UDPUkatonMission] = None
if use_ble:
    ukaton_mission = BLEUkatonMission()
else:
    ukaton_mission = UDPUkatonMission()


def on_connection():
    logger.debug("connected to device")


def on_disconnection():
    logger.debug("disconnected from device")


import asyncio


async def main():
    await ukaton_mission.connect(device_identifier)

    logger.debug("enabling sensor data...")
    await ukaton_mission.set_sensor_data_configuration({
        SensorType.MOTION: {
            MotionDataType.QUATERNION: 20,
        },
        SensorType.PRESSURE: {
            # PressureDataType.CENTER_OF_MASS: 20,
        }
    })
    logger.debug("enabled sensor data!")

    await asyncio.sleep(5)

asyncio.run(main())
