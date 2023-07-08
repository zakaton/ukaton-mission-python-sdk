import sys
sys.path.append(".")

from typing import Union, Tuple
from dataclasses import dataclass

import logging
logging.basicConfig()
logger = logging.getLogger("graph")
logger.setLevel(logging.ERROR)

import asyncio
import threading

# I used ChatGPT for the matplotlib stuff
import numpy as np
import quaternion
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
matplotlib.use("TkAgg")

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, PressureDataEventType, SensorDataConfigurations, SensorDataType, EventDispatcher, SensorDataEventType, SensorDataEventTypeTuple, Vector2, Vector3

use_ble = True
device_name = "missionDevice"
device_ip_address = "192.168.1.30"
device_identifier = device_name if use_ble else device_ip_address

ukaton_mission: Union[None, BLEUkatonMission, UDPUkatonMission] = None
if use_ble:
    ukaton_mission = BLEUkatonMission()
else:
    ukaton_mission = UDPUkatonMission()

data_rate = 20
sensor_data_configurations: SensorDataConfigurations = {
    SensorType.MOTION: {
        # MotionDataType.QUATERNION: data_rate,
        # MotionDataType.ROTATION_RATE: data_rate,
        # MotionDataType.LINEAR_ACCELERATION: data_rate,
    },
    SensorType.PRESSURE: {
        PressureDataType.PRESSURE_SINGLE_BYTE: data_rate,
    }
}
sensor_data_events: dict[SensorType, list[SensorDataEventType]] = {
    # SensorType.MOTION: list(sensor_data_configurations[SensorType.MOTION].keys()),
    SensorType.MOTION: [
        # MotionDataEventType.EULER,
        # MotionDataEventType.LINEAR_ACCELERATION,
    ],
    SensorType.PRESSURE: [
        PressureDataEventType.CENTER_OF_MASS,
        PressureDataEventType.HEEL_TO_TOE,
        PressureDataEventType.MASS,
    ]
}

N = 100
x = np.linspace(0, N, N)
sensor_data_event_types: list[SensorDataEventTypeTuple] = []


class LineData:
    def __init__(self):
        self.x: list[float] = [0] * N
        self.y: list[float] = [0] * N

    def __iter__(self):
        yield self.x
        yield self.y


lines_data: dict[SensorDataEventTypeTuple, list[LineData]] = {}

for sensor_type in sensor_data_events:
    for sensor_data_event_type in sensor_data_events[sensor_type]:
        sensor_data_event_type_tuple = (
            sensor_type, sensor_data_event_type)
        lines_data[sensor_data_event_type_tuple] = LineData()
        sensor_data_event_types.append(sensor_data_event_type_tuple)

        def event_listener(value, timestamp, sensor_type=sensor_type, sensor_data_event_type=sensor_data_event_type): return add_data(
            sensor_type, sensor_data_event_type, value, timestamp)
        event_dispatcher: EventDispatcher = ukaton_mission.motion_data_event_dispatcher if sensor_type is SensorType.MOTION else ukaton_mission.pressure_data_event_dispatcher
        event_dispatcher.add_event_listener(
            sensor_data_event_type, event_listener)

number_of_sensor_data_event_types = len(sensor_data_event_types)


def update_plot(frames):
    if ukaton_mission.is_connected:
        for i, ax in enumerate(axes.flatten()):
            if i >= number_of_sensor_data_event_types:
                continue

            sensor_type, sensor_data_event_type = sensor_data_event_types[i]
            _lines = lines[i]
            line_data = lines_data[(sensor_type, sensor_data_event_type)]

            for j, line in enumerate(_lines):
                # print(f"{line_data[j].y}")
                # line.set_data(line_data[j].x, line_data[j].y)
                line.set_data(x, line_data[j].y)

    return lines


def add_data(sensor_type: SensorType, sensor_data_event_type: SensorDataEventType, value: any, timestamp: int):

    logger.debug(
        f"[{timestamp}] adding data {sensor_type.name}:{sensor_data_event_type.name}, {value}")
    line_data_list = lines_data[(sensor_type, sensor_data_event_type)]

    values: list[float] = []
    match (sensor_type, sensor_data_event_type):
        case (SensorType.MOTION, MotionDataEventType.ACCELERATION | MotionDataEventType.LINEAR_ACCELERATION | MotionDataEventType.GRAVITY | MotionDataEventType.MAGNETOMETER | MotionDataEventType.GRAVITY | MotionDataEventType.EULER | MotionDataEventType.ROTATION_RATE):
            vector3: Vector3 = value
            values = list(vector3)
        case (SensorType.MOTION, MotionDataEventType.QUATERNION):
            q: np.quaternion = value
            values = list(quaternion.as_float_array(q))
        case (SensorType.PRESSURE, PressureDataEventType.CENTER_OF_MASS):
            vector2: Vector2 = value
            values = list(vector2)
            pass
        case (SensorType.PRESSURE, PressureDataEventType.HEEL_TO_TOE):
            heel_to_toe: float = value
            values.append(heel_to_toe)
        case (SensorType.PRESSURE, PressureDataEventType.MASS):
            mass: float = value
            values.append(mass)
        case _:
            pass

    for i, value in enumerate(values):
        x, y = line_data_list[i]
        x.append(timestamp)
        y.append(value)
        x = x[-N:]
        y = y[-N:]
        line_data_list[i].x = x
        line_data_list[i].y = y


# Number of rows and columns in the grid
num_rows = 2
num_cols = 2


fig, axes = plt.subplots(num_rows, num_cols, constrained_layout=True)
# fig, axes = plt.subplots(number_of_sensor_data_event_types, constrained_layout=True)
lines = []

# Initialize the lines for each subplot
for i, ax in enumerate(axes.flatten()):
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    if i >= number_of_sensor_data_event_types:
        ax.set_axis_off()
        continue

    sensor_type, sensor_data_event_type = sensor_data_event_types[i]
    sensor_data_event_type_name = sensor_data_event_type.name.lower()
    print(
        f"sensor_data_event_type_name: {sensor_data_event_type_name}")
    ax.set_title(sensor_data_event_type_name)
    ax.set_xlim(0, N)

    lines_to_append = []
    match (sensor_type, sensor_data_event_type):
        case (SensorType.MOTION, MotionDataEventType.ACCELERATION | MotionDataEventType.LINEAR_ACCELERATION | MotionDataEventType.GRAVITY | MotionDataEventType.MAGNETOMETER | MotionDataEventType.GRAVITY):
            line_x, = ax.plot([], [], label='x')
            line_y, = ax.plot([], [], label='y')
            line_z, = ax.plot([], [], label='z')
            lines_to_append += [line_x, line_y, line_z]
            match sensor_data_event_type:
                case MotionDataEventType.MAGNETOMETER:
                    ax.set_ylim(-100, 100)
                case _:
                    ax.set_ylim(-20, 20)
        case (SensorType.MOTION, MotionDataEventType.QUATERNION):
            line_w, = ax.plot([], [], label='w')
            line_x, = ax.plot([], [], label='x')
            line_y, = ax.plot([], [], label='y')
            line_z, = ax.plot([], [], label='z')
            lines_to_append += [line_w, line_x, line_y, line_z]
            ax.set_ylim(-1, 1)
        case (SensorType.MOTION, MotionDataEventType.EULER | MotionDataEventType.ROTATION_RATE):
            line_roll, = ax.plot([], [], label='roll')
            line_yaw, = ax.plot([], [], label='yaw')
            line_pitch, = ax.plot([], [], label='pitch')
            lines_to_append += [line_roll, line_yaw, line_pitch]
            ax.set_ylim(-2 * np.pi, 2 * np.pi)
        case (SensorType.PRESSURE, PressureDataEventType.CENTER_OF_MASS):
            line_x, = ax.plot([], [], label='x')
            line_y, = ax.plot([], [], label='y')
            lines_to_append += [line_x, line_y]
            ax.set_ylim(0, 1)
        case (SensorType.PRESSURE, PressureDataEventType.HEEL_TO_TOE):
            line_heel_to_toe, = ax.plot([], [], label='heel to toe')
            lines_to_append += [line_heel_to_toe]
            ax.set_ylim(0, 1)
        case (SensorType.PRESSURE, PressureDataEventType.MASS):
            line_mass, = ax.plot([], [], label='mass')
            lines_to_append += [line_mass]
            ax.set_ylim(0, 1)
        case _:
            pass

    lines_data[(sensor_type, sensor_data_event_type)] = []
    for i in range(0, len(lines_to_append)):
        lines_data[(sensor_type, sensor_data_event_type)].append(LineData())
    lines.append(lines_to_append)
    ax.legend(loc="upper left")


async def main():
    logger.info("attempting to connect...")
    await ukaton_mission.connect(device_identifier)
    if ukaton_mission.is_connected:
        logger.info("connected!")
        logger.info(f"device_type: {ukaton_mission.device_type.name}")

        logger.info("enabling sensor data...")
        await ukaton_mission.set_sensor_data_configurations(sensor_data_configurations)
        logger.info("enabled sensor data!")


def run_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main())
    loop.run_forever()


main_thread = threading.Thread(target=run_main)
main_thread.daemon = True
main_thread.start()

ani = FuncAnimation(fig, update_plot, frames=None,
                    interval=data_rate / 2)
# plt.ion()
plt.show()

# run_main_in_background()
main_thread.join()
