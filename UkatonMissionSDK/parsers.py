from UkatonMissionSDK.enumerations import *
from typing import Union, List
from dataclasses import dataclass
from collections import defaultdict
import struct
import math
import numpy as np
import quaternion

import logging

logging.basicConfig()
logger = logging.getLogger("parsers")
logger.setLevel(logging.ERROR)


@dataclass
class Vector2:
    x: float = 0
    y: float = 0

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, key):
        match key:
            case 0:
                return self.x
            case 1:
                return self.y
            case _:
                raise IndexError("Index out of Range")

    def __setitem__(self, key, value):
        match key:
            case 0:
                self.x = value
            case 1:
                self.y = value
            case _:
                raise IndexError("Index out of Range")


@dataclass
class Vector3(Vector2):
    z: float = 0

    def __iter__(self):
        yield from super().__iter__()
        yield self.z

    def __getitem__(self, key):
        match key:
            case 2:
                return self.z
            case _:
                return super().__getitem__(key)

    def __setitem__(self, key, value):
        match key:
            case 2:
                self.z = value
            case _:
                return super().__setitem__(key, value)


@dataclass
class PressureValue(Vector2):
    raw_value: float = 0
    normalized_value: float = 0


class PressureValueList(List[PressureValue]):
    def __init__(self, size: int = 0, pressure_data_type: PressureDataType = PressureDataType.PRESSURE_SINGLE_BYTE):
        super().__init__([PressureValue() for _ in range(size)])
        self.size: int = size
        self.pressure_data_type: PressureDataType = pressure_data_type
        self.is_single_byte: bool = pressure_data_type == PressureDataType.PRESSURE_SINGLE_BYTE
        self.sum: float = 0
        self.center_of_mass: Vector2 = Vector2()
        self.heel_to_toe: float = 0
        self.mass: float = 0
        self.scalar: float = pressure_data_scalars[self.pressure_data_type]

    def _update_sum(self):
        for value in self:
            self.sum += value.raw_value

    def _update_normalized_values(self):
        for value in self:
            value.normalized_value = value.normalized_value / self.sum if self.sum > 0 else 0

    def _update_center_of_mass(self):
        x, y = 0, 0
        for value in self:
            x += value.normalized_value * value.x
            y += value.normalized_value * value.y
        self.center_of_mass.x = x
        self.center_of_mass.y = y

    def _update_heel_to_toe(self):
        self.heel_to_toe = 1 - self.center_of_mass.y

    def _update_mass(self):
        self.mass = self.sum * self.scalar / self.size

    def update(self):
        self._update_sum()
        self._update_normalized_values()
        self._update_center_of_mass()
        self._update_heel_to_toe()
        self._update_mass()


def return_1(): return 1


motion_data_scalars: dict[MotionDataType, float] = defaultdict(return_1, {
    MotionDataType.ACCELERATION: 2 ** -8,
    MotionDataType.GRAVITY: 2 ** -8,
    MotionDataType.LINEAR_ACCELERATION: 2 ** -8,
    MotionDataType.ROTATION_RATE: 2 ** -9,
    MotionDataType.MAGNETOMETER: 2 ** -4,
    MotionDataType.QUATERNION: 2 ** -14
})
pressure_data_scalars: dict[PressureDataType, float] = defaultdict(return_1, {
    PressureDataType.PRESSURE_SINGLE_BYTE: 1 / 2 ** 8,
    PressureDataType.PRESSURE_DOUBLE_BYTE: 1 / 2 ** 12,
    PressureDataType.MASS: 1 / 2 ** 16,
})

pressure_positions: list[Vector2] = list(map(lambda l: Vector2(*l), [
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
]))

for v in pressure_positions:
    v.x /= 93.257
    v.y /= 265.069


def get_pressure_position(index: int, device_type: DeviceType) -> Vector2:
    x, y = pressure_positions[index]
    if device_type == DeviceType.RIGHT_INSOLE:
        x = 1 - x
    return Vector2(x, y)


PressureDataConfiguration = dict[PressureDataType, int]
MotionDataConfiguration = dict[MotionDataType, int]
SensorDataConfiguration = Union[MotionDataConfiguration,
                                PressureDataConfiguration]
SensorDataConfigurations = dict[SensorType, SensorDataConfiguration]


def serialize_sensor_data_configurations(configurations: SensorDataConfigurations) -> bytearray:
    serialized_configurations = bytearray()
    for sensor_type in configurations:
        _serialized_configurations = bytearray()
        configuration = configurations[sensor_type]
        for data_type in configuration:
            _serialized_configurations.append(data_type)
            data_rate = configuration[data_type]
            _serialized_configurations += data_rate.to_bytes(
                2, byteorder="little")
        size = len(_serialized_configurations)
        if size > 0:
            serialized_configurations.append(sensor_type)
            serialized_configurations.append(len(_serialized_configurations))
            serialized_configurations += _serialized_configurations
    logger.debug(f"serialized_configurations: {serialized_configurations}")
    return serialized_configurations


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


def get_float_32(data: bytearray, byte_offset: int = 0) -> float:
    return struct.unpack('<f', data[byte_offset:byte_offset + 4])[0]


def get_float_64(data: bytearray, byte_offset: int = 0) -> float:
    return struct.unpack('<d', data[byte_offset:byte_offset + 8])[0]


def get_uint_32(data: bytearray, byte_offset: int = 0) -> int:
    return struct.unpack('<L', data[byte_offset:byte_offset + 4])[0]
