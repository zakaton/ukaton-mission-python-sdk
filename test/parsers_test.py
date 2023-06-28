import sys
sys.path.append(".")

from ukaton_mission.parsers import *

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
