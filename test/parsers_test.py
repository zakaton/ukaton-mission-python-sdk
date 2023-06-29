import sys
sys.path.append(".")

from UkatonMissionSDK.parsers import *
from UkatonMissionSDK import BLEUkatonMission

import numpy as np
import quaternion
import struct

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
quat = quaternion.from_euler_angles(1, 0, 0)
print(quat)
print(quaternion.as_euler_angles(quat))

print(get_pressure_position(0, False))
p = PressureValueList(5)
print(p)

print(list(struct.iter_unpack('f', bytearray([1, 2, 3, 5]))))

l = [100, 200, 300, 400, 500]


def fun(pair):
    key, value = pair
    print(value)
    return value


l = list(map(fun, enumerate(l)))
print(l)
