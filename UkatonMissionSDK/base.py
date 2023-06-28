import abc
import time
from UkatonMissionSDK.utils import *
from UkatonMissionSDK.enumerations import *
from UkatonMissionSDK.parsers import *
import numpy as np
import quaternion
from typing import Union


class BaseUkatonMission(abc.ABC):
    number_of_pressure_sensors = 16

    def __init__(self):
        self.event_dispatcher: EventDispatcher = EventDispatcher(EventType)
        self.device_type: DeviceType = DeviceType.MOTION_MODULE
        self.device_name: str = ""
        self.battery_level: int = 0
        self.pressure_data: dict[PressureDataType, Union[list, float, Vector2]] = {
            PressureDataType.PRESSURE_SINGLE_BYTE: [0] * self.__class__.number_of_pressure_sensors,
            PressureDataType.PRESSURE_DOUBLE_BYTE: [0] * self.__class__.number_of_pressure_sensors,
            PressureDataType.CENTER_OF_MASS: [0, 0],
            PressureDataType.MASS: 0,
            PressureDataType.HEEL_TO_TOE: [0, 0],
        }
        self.motion_data: dict[MotionDataType, Union[Vector3, np.quaternion]] = {
            MotionDataType.ACCELERATION: [0, 0, 0],
            MotionDataType.GRAVITY: [0, 0, 0],
            MotionDataType.LINEAR_ACCELERATION: [0, 0, 0],
            MotionDataType.ROTATION_RATE: [0, 0, 0],
            MotionDataType.MAGNETOMETER: [0, 0, 0],
            MotionDataType.QUATERNION: np.quaternion()
        }
        self._last_time_received_sensor_data: int = 0
        self._sensor_data_timestamp_offset: int = 0

    @abc.abstractmethod
    def connect(self, identifier: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError()

    def set_sensor_data_configuration(self, sensor_data_configuration: dict[str, dict[str, int]]):
        serialized_sensor_data_configuration = serialize_sensor_data_configuration(
            sensor_data_configuration)
        self._send_sensor_data_configuration(
            serialized_sensor_data_configuration)

    @abc.abstractmethod
    def _send_sensor_data_configuration(self, sensor_data_configuration: dict[str, dict[str, int]]):
        raise NotImplementedError()

    def parse_sensor_data(self, data: bytearray, byte_offset: int = 0) -> int:
        self._last_time_received_sensor_data = time.time()
        raw_timestamp = get_uint_16(data, byte_offset)
        if raw_timestamp < self._last_time_received_sensor_data:
            self._sensor_data_timestamp_offset += 2 ** 16
        self._last_raw_sensor_data_timestamp = raw_timestamp
        timestamp = raw_timestamp + self._sensor_data_timestamp_offset
        byte_offset += 2
        print(f"timestamp: {timestamp}")

        data_len = len(data)
        while byte_offset < data_len:
            sensor_type = SensorType(data[byte_offset])
            byte_offset += 1
            print(f"sensor_type: {sensor_type}")
            byte_offset = self._parse_sensor_data_type(
                data, byte_offset, timestamp, sensor_type)

        return byte_offset

    def _parse_sensor_data_type(self, data: bytearray, byte_offset: int, timestamp: int, sensor_type: SensorType) -> int:
        data_size = data[byte_offset]
        byte_offset += 1
        print(f"data_size: {data_size}")

        final_byte_offset = byte_offset + final_byte_offset

        match sensor_type:
            case SensorType.Motion:
                byte_offset = self._parse_motion_data(
                    data, byte_offset, final_byte_offset, timestamp)
            case SensorType.PRESSURE:
                byte_offset = self._parse_pressure_data(
                    data, byte_offset, final_byte_offset, timestamp)
            case _:
                print(f'undefined sensor_type "{sensor_type}')

        return byte_offset

    def _parse_motion_data(data: bytearray, byte_offset: int, final_byte_offset: int, timestamp: int):
        # FILL
        while byte_offset < final_byte_offset:
            motion_sensor_data_type = MotionDataType(data[byte_offset])
            byte_offset += 1
            print(f'motion_sensor_data_type: {motion_sensor_data_type}')

            scalar = motion_data_scalars[motion_sensor_data_type]

            match motion_sensor_data_type:
                case MotionDataType.ACCELERATION, MotionDataType.GRAVITY, MotionDataType.LINEAR_ACCELERATION, MotionDataType.MAGNETOMETER:
                    byte_offset += 6

                    pass
                case MotionDataType.ROTATION_RATE:
                    byte_offset += 6
                    pass
                case MotionDataType.QUATERNION:
                    byte_offset += 8
                    pass

                case _:
                    print(
                        f'undefined motion_sensor_data_type: {motion_sensor_data_type}')

        return byte_offset

    def _parse_pressure_data(data: bytearray, byte_offset: int, final_byte_offset: int, timestamp: int):
        # FILL
        while byte_offset < final_byte_offset:
            pressure_sensor_data_type = PressureDataType(data[byte_offset])
            byte_offset += 1
            print(f'pressure_sensor_data_type: {pressure_sensor_data_type}')

            scalar = pressure_data_scalars[pressure_sensor_data_type] or 1

            match pressure_sensor_data_type:
                case PressureDataType.PRESSURE_SINGLE_BYTE, PressureDataType.PRESSURE_DOUBLE_BYTE:
                    pass
                case PressureDataType.CENTER_OF_MASS:
                    pass
                case PressureDataType.MASS:
                    pass
                case PressureDataType.HEEL_TO_TOE:
                    pass
                case _:
                    print(
                        f'undefined pressure_sensor_data_type: {pressure_sensor_data_type}')

        return byte_offset

    @abc.abstractmethod
    def _send_vibration(self, vibration: bytearray):
        raise NotImplementedError()


class BaseUkatonMissions(abc.ABC):
    pass
