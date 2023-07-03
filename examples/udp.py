import sys
sys.path.append(".")

import asyncio

import logging
logging.basicConfig()
logger = logging.getLogger("udp example")
logger.setLevel(logging.DEBUG)

from UkatonMissionSDK import UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType

ukaton_mission = UDPUkatonMission()


def on_connection():
    logger.debug("connected callback triggered :)")


def on_disconnection():
    logger.debug("disconnected callback triggered :O")


async def main():
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.CONNECTED, on_connection)
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.DISCONNECTED, on_disconnection)

    await ukaton_mission.connect("192.168.1.30")

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
    logger.debug("end of main ;)")

asyncio.run(main())
