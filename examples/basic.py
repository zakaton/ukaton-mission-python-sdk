import sys
sys.path.append(".")

from typing import Union

import logging
logging.basicConfig()
logger = logging.getLogger("basic")
logger.setLevel(logging.DEBUG)

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, SensorDataConfigurations

use_ble = True
device_name = "missionDevice"
device_ip_address = "192.168.1.30"
device_identifier = device_name if use_ble else device_ip_address

ukaton_mission: Union[None, BLEUkatonMission, UDPUkatonMission] = None
if use_ble:
    ukaton_mission = BLEUkatonMission()
else:
    ukaton_mission = UDPUkatonMission()

import asyncio
import threading


def on_connection():
    logger.debug("connected callback triggered :)")


def on_disconnection():
    logger.debug("disconnected callback triggered :O")


def on_quaternion_data(quaternion, timestamp):
    logger.debug(f"[{timestamp}]: {quaternion}")


ukaton_mission.connection_event_dispatcher.add_event_listener(
    ConnectionEventType.CONNECTED, on_connection)
ukaton_mission.connection_event_dispatcher.add_event_listener(
    ConnectionEventType.DISCONNECTED, on_disconnection)
ukaton_mission.motion_data_event_dispatcher.add_event_listener(
    MotionDataEventType.QUATERNION, on_quaternion_data)

sensor_data_configurations: SensorDataConfigurations = {
    SensorType.MOTION: {
        MotionDataType.QUATERNION: 20,
    },
    SensorType.PRESSURE: {
        # PressureDataType.CENTER_OF_MASS: 20,
    }
}


async def main():
    logger.debug("attempting to connect...")
    await ukaton_mission.connect(device_identifier)
    logger.debug(f"connected? {ukaton_mission.is_connected}")
    if ukaton_mission.is_connected:
        logger.debug("enabling sensor data...")
        await ukaton_mission.set_sensor_data_configurations(sensor_data_configurations)
        logger.debug("enabled sensor data!")


def run_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main())
    loop.run_forever()


main_thread = threading.Thread(target=run_main)
# main_thread.daemon = True
main_thread.start()
