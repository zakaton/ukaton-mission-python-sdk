from UkatonMissionSDK.enumerations import *
from typing import Union
from collections import namedtuple

import math
import numpy as np
import quaternion

Vector2 = namedtuple("Vector2", ["x", "y"])
Vector3 = namedtuple("Vector3", ["x", "y", "z"])

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

pressure_positions: list[Vector2] = [
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


def parse_motion_vector(data: bytearray, byte_offset: int = 0, scalar: float = 1, device_type: DeviceType = DeviceType.MOTION_MODULE) -> Vector3:
    x = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    y = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    z = get_int_16(data, byte_offset) * scalar
    byte_offset += 2

    vector = None
    if device_type == DeviceType.MOTION_MODULE:
        vector = [-y, z, x]
    else:
        if device_type == DeviceType.RIGHT_INSOLE:
            vector = [z, -x, y]
        else:
            vector = [-z, -x, -y]

    return vector


def parse_motion_euler(data: bytearray, byte_offset: int = 0, scalar: float = 1, device_type: DeviceType = DeviceType.MOTION_MODULE) -> Vector3:
    x = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    y = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    z = get_int_16(data, byte_offset) * scalar
    byte_offset += 2

    euler = None
    if device_type == DeviceType.MOTION_MODULE:
        euler = [y, -z, -x]
    else:
        if device_type == DeviceType.RIGHT_INSOLE:
            euler = [-z, x, -y]
        else:
            euler = [z, x, y]

    return euler


insole_correction_quaternions: dict[DeviceType, np.quaternion] = {
    DeviceType.LEFT_INSOLE: quaternion.from_euler_angles(0, math.pi / 2, -math.pi / 2),
    DeviceType.RIGHT_INSOLE: quaternion.from_euler_angles(
        -math.pi / 2, -math.pi / 2, 0)
}
correction_quaternions: dict[DeviceType, np.quaternion] = {
    DeviceType.MOTION_MODULE: quaternion.from_euler_angles(0, -math.pi / 2, 0),
    DeviceType.LEFT_INSOLE: quaternion.from_euler_angles(0, math.pi, 0),
    DeviceType.RIGHT_INSOLE: quaternion.from_euler_angles(0, math.pi, 0),
}


def parse_motion_quaternion(data: bytearray, byte_offset: int = 0, scalar: float = 1, device_type: DeviceType = DeviceType.MOTION_MODULE) -> np.quaternion:
    w = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    x = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    y = get_int_16(data, byte_offset) * scalar
    byte_offset += 2
    z = get_int_16(data, byte_offset) * scalar
    byte_offset += 2

    quaternion = np.quaternion(-y, -w, -x, z)
    if device_type != DeviceType.MOTION_MODULE:
        quaternion *= insole_correction_quaternions[device_type]
    quaternion *= correction_quaternions[device_type]

    return quaternion


def get_int_16(data: bytearray, byte_offset: int = 0) -> int:
    return int.from_bytes(data[byte_offset:byte_offset + 2], byteorder="little", signed=True)


def get_uint_16(data: bytearray, byte_offset: int = 0) -> int:
    return int.from_bytes(data[byte_offset:byte_offset + 2], byteorder="little", signed=False)
