from enum import Enum, IntEnum


class EventType(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class DeviceType(IntEnum):
    MOTION_MODULE = 0
    LEFT_INSOLE = 1
    RIGHT_INSOLE = 2


class SensorType(IntEnum):
    MOTION = 0
    PRESSURE = 1


class MotionDataType(IntEnum):
    ACCELERATION = 0
    GRAVITY = 1
    LINEAR_ACCELERATION = 2
    ROTATION_RATE = 3
    MAGNETOMETER = 4
    QUATERNION = 5


class PressureDataType(IntEnum):
    PRESSURE_SINGLE_BYTE = 0
    PRESSURE_DOUBLE_BYTE = 1
    CENTER_OF_MASS = 2
    MASS = 3
    HEEL_TO_TOE = 4


class VibrationType(IntEnum):
    WAVEFORM = 0
    SEQUENCE = 1
