from enum import Enum, IntEnum, auto


class EventType(IntEnum):
    CONNECTED = auto()
    DISCONNECTED = auto()


class DeviceType(IntEnum):
    MOTION_MODULE = auto()
    LEFT_INSOLE = auto()
    RIGHT_INSOLE = auto()


class SensorType(IntEnum):
    MOTION = auto()
    PRESSURE = auto()


class MotionDataType(IntEnum):
    ACCELERATION = auto()
    GRAVITY = auto()
    LINEAR_ACCELERATION = auto()
    ROTATION_RATE = auto()
    MAGNETOMETER = auto()
    QUATERNION = auto()
    EULER = auto()


class PressureDataType(IntEnum):
    PRESSURE_SINGLE_BYTE = auto()
    PRESSURE_DOUBLE_BYTE = auto()
    CENTER_OF_MASS = auto()
    MASS = auto()
    HEEL_TO_TOE = auto()


class VibrationType(IntEnum):
    WAVEFORM = auto()
    SEQUENCE = auto()


class UDPMessageType(IntEnum):
    PING = auto()
    BATTERY_LEVEL = auto()

    GET_TYPE = auto()
    SET_TYPE = auto()

    GET_NAME = auto()
    SET_NAME = auto()

    MOTION_CALIBRATION = auto()

    GET_SENSOR_DATA_CONFIGURATIONS = auto()
    SET_SENSOR_DATA_CONFIGURATIONS = auto()

    SENSOR_DATA = auto()
