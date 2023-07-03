import sys
sys.path.append(".")

from typing import Union

import logging
logging.basicConfig()
logger = logging.getLogger("basic")
logger.setLevel(logging.DEBUG)

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType

use_ble = True
device_name = "missionDevice"
device_ip_address = "0.0.0.0"
device_identifier = device_name if use_ble else device_ip_address

ukaton_mission: Union[None, BLEUkatonMission, UDPUkatonMission] = None
if use_ble:
    ukaton_mission = BLEUkatonMission()
else:
    ukaton_mission = UDPUkatonMission()


import asyncio


def on_connection():
    logger.debug("connected callback triggered :)")


def on_disconnection():
    logger.debug("disconnected callback triggered :O")


async def main():
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.CONNECTED, on_connection)
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.DISCONNECTED, on_disconnection)

    await ukaton_mission.connect(device_identifier)

    logger.debug("triggering vibration...")
    await ukaton_mission.vibrate_waveform([1, 2, 3])
    logger.debug("triggered vibration!")

    logger.debug("enabling sensor data...")
    await ukaton_mission.set_sensor_data_configuration({
        SensorType.MOTION: {
            # MotionDataType.QUATERNION: 20,
        },
        SensorType.PRESSURE: {
            PressureDataType.CENTER_OF_MASS: 20,
        }
    })
    logger.debug("enabled sensor data!")

    await asyncio.sleep(5)
    await ukaton_mission.disconnect()
    logger.debug("end of main ;)")

asyncio.run(main())
