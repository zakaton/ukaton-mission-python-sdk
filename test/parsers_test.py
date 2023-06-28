import sys
sys.path.append(".")

from UkatonMissionSDK.parsers import *
from UkatonMissionSDK import BLEUkatonMission

import numpy as np
import quaternion

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
print(parse_motion_quaternion(
    bytearray([1, 0, 2, 0, 3, 0, 4, 0])))
print(quaternion.from_euler_angles(1, 0, 0))
