import sys
MIN_PYTHON = (3, 10)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

from UkatonMissionSDK.base import BaseUkatonMission, BaseUkatonMissions
from UkatonMissionSDK.udp import UDPUkatonMission, UDPUkatonMissions
from UkatonMissionSDK.ble import BLEUkatonMission, BLEUkatonMissions
from UkatonMissionSDK.enumerations import ConnectionEventType, MotionDataEventType, PressureDataEventType, SensorType, MotionDataType, PressureDataType, DeviceType, SensorDataType, sensor_data_type_to_sensor_data_event_type, SensorDataEventType, SensorDataEventTypeTuple, ConnectionType
UkatonMission: dict[ConnectionType, BaseUkatonMission] = {
    ConnectionType.BLE: BLEUkatonMission,
    ConnectionType.UDP: UDPUkatonMission,
}
UkatonMissiosn: dict[ConnectionType, BaseUkatonMissions] = {
    ConnectionType.BLE: BLEUkatonMissions,
    ConnectionType.UDP: UDPUkatonMissions,
}
from UkatonMissionSDK.parsers import SensorDataConfigurations, Vector2, Vector3, Quaternion, PressureValueList, PressureValue
from UkatonMissionSDK.utils import EventDispatcher
