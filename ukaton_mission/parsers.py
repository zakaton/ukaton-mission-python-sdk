from ukaton_mission.enumerations import *

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

pressure_positions: list[list[float]] = [
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
