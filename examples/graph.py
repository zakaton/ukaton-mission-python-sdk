import sys
sys.path.append(".")

from typing import Union
from dataclasses import dataclass
import functools

import logging
logging.basicConfig()
logger = logging.getLogger("graph")
logger.setLevel(logging.DEBUG)

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, PressureDataEventType, SensorDataConfigurations, SensorDataType, EventDispatcher, SensorDataEventType

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


def on_connection():
    logger.debug("connected callback triggered :)")


def on_disconnection():
    logger.debug("disconnected callback triggered :O")


@dataclass
class Datum:
    value: any
    timestamp: int


N = 20
data: dict[SensorType: dict[SensorDataEventType: list[Datum]]] = {}


def add_data(sensor_type: SensorType, sensor_data_event_type: SensorDataEventType, value: any, timestamp: int):
    logger.debug(
        f"[{timestamp}] adding data {sensor_type.name}:{sensor_data_event_type.name}, {value}")
    datum = Datum(value, timestamp)
    _data: list[Datum] = data[sensor_type][sensor_data_event_type]
    _data.append(datum)
    _data = _data[-N:]
    print(len(_data))


async def main():
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.CONNECTED, on_connection)
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.DISCONNECTED, on_disconnection)

    await ukaton_mission.connect(device_identifier)

    logger.debug("enabling sensor data...")
    sensor_data_configurations: SensorDataConfigurations = {
        SensorType.MOTION: {
            # MotionDataType.QUATERNION: 20,
            # MotionDataType.ACCELERATION: 20,
        },
        SensorType.PRESSURE: {
            PressureDataType.PRESSURE_SINGLE_BYTE: 20,
        }
    }
    sensor_data_events: dict[SensorType, list[SensorDataEventType]] = {
        SensorType.MOTION: [],
        SensorType.PRESSURE: [PressureDataEventType.CENTER_OF_MASS]
    }
    for sensor_type in sensor_data_events:
        data[sensor_type] = {}
        for sensor_data_event_type in sensor_data_events[sensor_type]:
            data[sensor_type][sensor_data_event_type] = []

            def event_listener(value, timestamp, sensor_type=sensor_type, sensor_data_event_type=sensor_data_event_type): return add_data(
                sensor_type, sensor_data_event_type, value, timestamp)
            event_dispatcher: EventDispatcher = ukaton_mission.motion_data_event_dispatcher if sensor_type is SensorType.MOTION else ukaton_mission.pressure_data_event_dispatcher
            event_dispatcher.add_event_listener(
                sensor_data_event_type, event_listener)

    await ukaton_mission.set_sensor_data_configurations(sensor_data_configurations)
    logger.debug("enabled sensor data!")

    await asyncio.sleep(1)

asyncio.run(main())
