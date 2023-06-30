from enum import IntEnum, auto


class ConnectionEventType(IntEnum):
    CONNECTED = 0
    DISCONNECTED = auto()


class PressureDataEventType(IntEnum):
    PRESSURE = 0
    CENTER_OF_MASS = auto()
    MASS = auto()
    HEEL_TO_TOE = auto()


class MotionDataEventType(IntEnum):
    ACCELERATION = 0
    GRAVITY = auto()
    LINEAR_ACCELERATION = auto()
    ROTATION_RATE = auto()
    MAGNETOMETER = auto()
    QUATERNION = auto()
    EULER = auto()


class DeviceType(IntEnum):
    MOTION_MODULE = 0
    LEFT_INSOLE = auto()
    RIGHT_INSOLE = auto()


class SensorType(IntEnum):
    MOTION = 0
    PRESSURE = auto()


class MotionDataType(IntEnum):
    ACCELERATION = 0
    GRAVITY = auto()
    LINEAR_ACCELERATION = auto()
    ROTATION_RATE = auto()
    MAGNETOMETER = auto()
    QUATERNION = auto()
    EULER = auto()


class PressureDataType(IntEnum):
    PRESSURE_SINGLE_BYTE = 0
    PRESSURE_DOUBLE_BYTE = auto()
    CENTER_OF_MASS = auto()
    MASS = auto()
    HEEL_TO_TOE = auto()


class VibrationType(IntEnum):
    WAVEFORM = 0
    SEQUENCE = auto()


class UDPMessageType(IntEnum):
    PING = 0
    BATTERY_LEVEL = auto()

    GET_TYPE = auto()
    SET_TYPE = auto()

    GET_NAME = auto()
    SET_NAME = auto()

    MOTION_CALIBRATION = auto()

    GET_SENSOR_DATA_CONFIGURATIONS = auto()
    SET_SENSOR_DATA_CONFIGURATIONS = auto()

    SENSOR_DATA = auto()
