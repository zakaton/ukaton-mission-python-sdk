import sys
sys.path.append(".")

from typing import Union
import tkinter as tk
from PIL import Image, ImageTk

import logging
logging.basicConfig()
logger = logging.getLogger("pressure")
logger.setLevel(logging.ERROR)

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, PressureDataType, BLEUkatonMissions, PressureDataEventType, SensorDataConfigurations, DeviceType, PressureValueList, Vector2

use_ble = False
device_name = "missionDevice"
device_ip_address = "192.168.1.30"
device_identifier = device_name if use_ble else device_ip_address

ukaton_mission: Union[None, BLEUkatonMission, UDPUkatonMission] = None
if use_ble:
    ukaton_mission = BLEUkatonMission()
else:
    ukaton_mission = UDPUkatonMission()

import asyncio
import threading

sensor_data_configurations: SensorDataConfigurations = {
    SensorType.PRESSURE: {
        PressureDataType.PRESSURE_SINGLE_BYTE: 20
    }
}


def on_pressure_data(pressure_values: PressureValueList, timestamp: int):
    if not did_setup_window:
        return

    for i, pressure_value in enumerate(pressure_values):
        opacity = pressure_value.normalized_value
        red = int(opacity * 255)
        fill_color = f"#{red:02x}0000"
        canvas.itemconfig(squares[i], fill=fill_color)


ukaton_mission.pressure_data_event_dispatcher.add_event_listener(
    PressureDataEventType.PRESSURE, on_pressure_data)


async def main():
    logger.info("connecting to device...")
    await ukaton_mission.connect(device_identifier)
    if ukaton_mission.is_connected:
        logger.info("connected!")

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

# I used ChatGPT for the tkinter window stuff...

# without this the image will be removed due to garbage collection
background_photo = None
squares = []
canvas = None
did_setup_window = False


def setup_window():
    global did_setup_window
    if did_setup_window:
        return
    did_setup_window = True

    global background_photo
    global canvas
    image_dimensions = Vector2(265, 753)
    image_scalar = 0.8
    image_dimensions.multiply_scalar(image_scalar)

    background_image = Image.open(
        "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk/assets/insole.png")
    background_image = background_image.resize(round(image_dimensions))
    if ukaton_mission.device_type is DeviceType.RIGHT_INSOLE:
        background_image = background_image.transpose(Image.FLIP_LEFT_RIGHT)
    background_photo = ImageTk.PhotoImage(background_image)

    canvas = tk.Canvas(window, width=image_dimensions.x,
                       height=image_dimensions.y)
    canvas.pack()

    canvas.create_image(0, 0, anchor=tk.NW, image=background_photo)

    square_dimensions_percent = Vector2(0.17, 0.06)
    square_dimensions = image_dimensions * square_dimensions_percent
    half_square_dimensions = square_dimensions * 0.5

    for i in range(ukaton_mission.number_of_pressure_sensors):
        pressure_position = ukaton_mission.get_pressure_position(i)
        square_position = image_dimensions * pressure_position
        square_position = square_position - half_square_dimensions
        square = canvas.create_rectangle(
            square_position.x, square_position.y, square_position.x + square_dimensions.x, square_position.y + square_dimensions.y, fill='black')
        squares.append(square)

    did_setup_window = True


ukaton_mission.connection_event_dispatcher.add_event_listener(
    ConnectionEventType.CONNECTED, setup_window, True)

window = tk.Tk()
# setup_window()
window.mainloop()
