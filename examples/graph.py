import sys
sys.path.append(".")

from typing import Union
from dataclasses import dataclass

import logging
logging.basicConfig()
logger = logging.getLogger("graph")
logger.setLevel(logging.DEBUG)

import asyncio
import threading

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


def on_connection():
    logger.debug("connected callback triggered :)")


def on_disconnection():
    logger.debug("disconnected callback triggered :O")


# I used ChatGPT for the matplotlib stuff
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
matplotlib.use("TkAgg")

# Number of rows and columns in the grid
num_rows = 1
num_cols = 2

fig, axes = plt.subplots(num_rows, num_cols)

lines = []

# Initialize the lines for each subplot
for ax in axes.flatten():
    line1, = ax.plot([], [], label='Sin')
    line2, = ax.plot([], [], label='Cos')
    line3, = ax.plot([], [], label='Tan')
    lines.append([line1, line2, line3])
    ax.legend()

# Data for the curves
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)


@dataclass
class Datum:
    value: any
    timestamp: int


N = 20
data: dict[SensorType: dict[SensorDataEventType: list[Datum]]] = {}


def update_plot(frames):
    for i, ax in enumerate(axes.flatten()):
        # Update the data for the curves
        y1_data = y1 + np.random.normal(0, 5, len(x))
        y2_data = y2 + np.random.normal(0, 0.1, len(x))
        y3_data = y3 + np.random.normal(0, 0.1, len(x))

        # Update the lines with new data
        lines[i][0].set_data(x, y1_data)
        lines[i][1].set_data(x, y2_data)
        lines[i][2].set_data(x, y3_data)

        # Set the y-axis limits to fit the data
        ax.set_ylim([np.min([y1_data, y2_data, y3_data]),
                     np.max([y1_data, y2_data, y3_data])])
    return lines


def add_data(sensor_type: SensorType, sensor_data_event_type: SensorDataEventType, value: any, timestamp: int):
    logger.debug(
        f"[{timestamp}] adding data {sensor_type.name}:{sensor_data_event_type.name}, {value}")
    datum = Datum(value, timestamp)
    _data: list[Datum] = data[sensor_type][sensor_data_event_type]
    _data.append(datum)
    _data = _data[-N:]
    print(len(_data))


async def main():
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.CONNECTED, on_connection)
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.DISCONNECTED, on_disconnection)

    await ukaton_mission.connect(device_identifier)

    logger.debug("enabling sensor data...")
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
    for sensor_type in sensor_data_events:
        data[sensor_type] = {}
        for sensor_data_event_type in sensor_data_events[sensor_type]:
            data[sensor_type][sensor_data_event_type] = []

            def event_listener(value, timestamp, sensor_type=sensor_type, sensor_data_event_type=sensor_data_event_type): return add_data(
                sensor_type, sensor_data_event_type, value, timestamp)
            event_dispatcher: EventDispatcher = ukaton_mission.motion_data_event_dispatcher if sensor_type is SensorType.MOTION else ukaton_mission.pressure_data_event_dispatcher
            event_dispatcher.add_event_listener(
                sensor_data_event_type, event_listener)

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
