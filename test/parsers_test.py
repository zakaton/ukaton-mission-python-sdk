import sys
sys.path.append(".")

from UkatonMissionSDK.parsers import *
from UkatonMissionSDK import BLEUkatonMission

configuration = serialize_sensor_data_configuration({
    SensorType.MOTION: {
        MotionDataType.QUATERNION: 20,
    },
    SensorType.PRESSURE: {
        PressureDataType.PRESSURE_DOUBLE_BYTE: 40
    },
})
l = list(configuration)
print(l)

ukaton_mission = BLEUkatonMission()
ukaton_mission.parse_sensor_data(bytearray([1, 0]))
