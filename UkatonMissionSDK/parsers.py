from UkatonMissionSDK.enumerations import *
from typing import Union
import math
import numpy

motion_data_scalars: dict[MotionDataType, float] = {
    MotionDataType.ACCELERATION: 2 ** -8,
    MotionDataType.GRAVITY: 2 ** -8,
    MotionDataType.LINEAR_ACCELERATION: 2 ** -8,
    MotionDataType.ROTATION_RATE: 2 ** -9,
    MotionDataType.MAGNETOMETER: 2 ** -4,
    MotionDataType.QUATERNION: 2 ** -14
}
pressure_data_scalars: dict[PressureDataType, float] = {
    PressureDataType.PRESSURE_SINGLE_BYTE: 1 / 2 ** 8,
    PressureDataType.PRESSURE_DOUBLE_BYTE: 1 / 2 ** 12,
    PressureDataType.MASS: 1 / 2 ** 16,
}

pressure_positions: list[list[float]] = [
    [59.55, 32.3],
    [33.1, 42.15],

    [69.5, 55.5],
    [44.11, 64.8],
    [20.3, 71.9],

    [63.8, 81.1],
    [41.44, 90.8],
    [19.2, 102.8],

    [48.3, 119.7],
    [17.8, 130.5],

    [43.3, 177.7],
    [18.0, 177.0],

    [43.3, 200.6],
    [18.0, 200.0],

    [43.5, 242.0],
    [18.55, 242.1]
]

pressure_positions = list(map(
    lambda v: [v[0] / 93.257, v[1] / 265.069], pressure_positions))


def serialize_sensor_data_configuration(configurations: dict[SensorType, dict[Union[MotionDataType, PressureDataType], int]]) -> bytearray:
    serialized_configuration = bytearray()
    for sensor_type in configurations:
        _serialized_configuration = bytearray()
        configuration = configurations[sensor_type]
        for data_type in configuration:
            _serialized_configuration.append(data_type)
            data_rate = configuration[data_type]
            _serialized_configuration += data_rate.to_bytes(
                2, byteorder="little")
        size = len(_serialized_configuration)
        if size > 0:
            serialized_configuration.append(sensor_type)
            serialized_configuration.append(len(_serialized_configuration))
            serialized_configuration += _serialized_configuration
    return serialized_configuration


def parse_motion_vector(data: bytearray, byte_offset: int, scalar: float) -> list[int]:
    vector = []
    return vector


def parse_motion_euler(data: bytearray, byte_offset: int, scalar: float) -> list[int]:
    euler = []
    return euler


def parse_motion_quaternion(data: bytearray, byte_offset: int, scalar: float) -> list[int]:
    quaternion = []
    return quaternion
