import sys
sys.path.append(".")

from typing import Union, Tuple
from dataclasses import dataclass

import logging
logging.basicConfig()
logger = logging.getLogger("graph")
logger.setLevel(logging.DEBUG)

import asyncio
import threading

# I used ChatGPT for the matplotlib stuff
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
matplotlib.use("TkAgg")

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, PressureDataEventType, SensorDataConfigurations, SensorDataType, EventDispatcher, SensorDataEventType

use_ble = True
device_name = "missionDevice"
device_ip_address = "192.168.1.30"
device_identifier = device_name if use_ble else device_ip_address

ukaton_mission: Union[None, BLEUkatonMission, UDPUkatonMission] = None
if use_ble:
    ukaton_mission = BLEUkatonMission()
else:
    ukaton_mission = UDPUkatonMission()

sensor_data_configurations: SensorDataConfigurations = {
    SensorType.MOTION: {
        MotionDataType.QUATERNION: 20,
        # MotionDataType.ACCELERATION: 20,
    },
    SensorType.PRESSURE: {
        # PressureDataType.PRESSURE_SINGLE_BYTE: 20,
    }
}
sensor_data_events: dict[SensorType, list[SensorDataEventType]] = {
    # SensorType.MOTION: list(sensor_data_configurations[SensorType.MOTION].keys()),
    SensorType.MOTION: [MotionDataEventType.QUATERNION],
    SensorType.PRESSURE: [PressureDataEventType.CENTER_OF_MASS]
}


@dataclass
class Datum:
    value: any
    timestamp: int


N = 20
data: dict[SensorType: dict[SensorDataEventType: list[Datum]]] = {}
sensor_data_event_types: list[Tuple[SensorType, SensorDataEventType]] = []

for sensor_type in sensor_data_events:
    data[sensor_type] = {}
    for sensor_data_event_type in sensor_data_events[sensor_type]:
        data[sensor_type][sensor_data_event_type] = []
        sensor_data_event_types.append((sensor_type, sensor_data_event_type))

        def event_listener(value, timestamp, sensor_type=sensor_type, sensor_data_event_type=sensor_data_event_type): return add_data(
            sensor_type, sensor_data_event_type, value, timestamp)
        event_dispatcher: EventDispatcher = ukaton_mission.motion_data_event_dispatcher if sensor_type is SensorType.MOTION else ukaton_mission.pressure_data_event_dispatcher
        event_dispatcher.add_event_listener(
            sensor_data_event_type, event_listener)

number_of_sensor_data_event_types = len(sensor_data_event_types)

# Data for the curves
x = np.linspace(0, 10, 100)


def update_plot(frames):
    for i, ax in enumerate(axes.flatten()):
        if i >= number_of_sensor_data_event_types:
            break

        sensor_type, sensor_data_event_type = sensor_data_event_types[i]
        # lines[i][2].set_data(x, y3_data)
        _data = data[sensor_type][sensor_data_event_type]
        match (sensor_type, sensor_data_event_type):
            case (SensorType.MOTION, MotionDataEventType.ACCELERATION | MotionDataEventType.LINEAR_ACCELERATION | MotionDataEventType.GRAVITY | MotionDataEventType.MAGNETOMETER | MotionDataEventType.GRAVITY):
                pass
            case (SensorType.MOTION, MotionDataEventType.QUATERNION):
                pass
            case (SensorType.MOTION, MotionDataEventType.EULER):
                pass
            case (SensorType.PRESSURE, PressureDataEventType.CENTER_OF_MASS):
                pass
            case (SensorType.PRESSURE, PressureDataEventType.HEEL_TO_TOE):
                pass
            case (SensorType.PRESSURE, PressureDataEventType.MASS):
                pass
            case _:
                pass

    return lines


def add_data(sensor_type: SensorType, sensor_data_event_type: SensorDataEventType, value: any, timestamp: int):
    logger.debug(
        f"[{timestamp}] adding data {sensor_type.name}:{sensor_data_event_type.name}, {value}")
    datum = Datum(value, timestamp)
    _data: list[Datum] = data[sensor_type][sensor_data_event_type]
    _data.append(datum)
    _data = _data[-N:]


# Number of rows and columns in the grid
num_rows = 2
num_cols = 2


# fig, axes = plt.subplots(num_rows, num_cols, constrained_layout=True)
fig, axes = plt.subplots(
    number_of_sensor_data_event_types, constrained_layout=True)
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
    print(f"sensor_data_event_type_name: {sensor_data_event_type_name}")
    ax.set_title(sensor_data_event_type_name)

    lines_to_append = []
    match (sensor_type, sensor_data_event_type):
        case (SensorType.MOTION, MotionDataEventType.ACCELERATION | MotionDataEventType.LINEAR_ACCELERATION | MotionDataEventType.GRAVITY | MotionDataEventType.MAGNETOMETER | MotionDataEventType.GRAVITY):
            line_x, = ax.plot([], [], label='x')
            line_y, = ax.plot([], [], label='y')
            line_z, = ax.plot([], [], label='z')
            lines_to_append += [line_x, line_y, line_z]
            ax.set_ylim(-1, 1)
        case (SensorType.MOTION, MotionDataEventType.QUATERNION):
            line_w, = ax.plot([], [], label='w')
            line_x, = ax.plot([], [], label='x')
            line_y, = ax.plot([], [], label='y')
            line_z, = ax.plot([], [], label='z')
            lines_to_append += [line_w, line_x, line_y, line_z]
            ax.set_ylim(-1, 1)
        case (SensorType.MOTION, MotionDataEventType.EULER):
            line_yaw, = ax.plot([], [], label='yaw')
            line_pitch, = ax.plot([], [], label='pitch')
            line_roll, = ax.plot([], [], label='roll')
            lines_to_append += [line_yaw, line_pitch, line_roll]
            ax.set_ylim(-1, 1)
        case (SensorType.PRESSURE, PressureDataEventType.CENTER_OF_MASS):
            line_x, = ax.plot([], [], label='x')
            line_y, = ax.plot([], [], label='y')
            lines_to_append += [line_x, line_y]
            ax.set_ylim(-1, 1)
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
    lines.append(lines_to_append)
    ax.legend()


async def main():
    logger.debug("attempting to connect...")
    await ukaton_mission.connect(device_identifier)
    if ukaton_mission.is_connected:
        logger.debug("connected!")

        logger.debug("enabling sensor data...")
        await ukaton_mission.set_sensor_data_configurations(sensor_data_configurations)
        logger.debug("enabled sensor data!")


def run_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main())
    loop.run_forever()


main_thread = threading.Thread(target=run_main)
main_thread.daemon = True
main_thread.start()

ani = FuncAnimation(fig, update_plot, frames=range(100), interval=20)
# plt.ion()
plt.show()

# run_main_in_background()
main_thread.join()
