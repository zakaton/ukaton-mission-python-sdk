import sys
sys.path.append(".")

from typing import Union
import tkinter as tk
from PIL import Image, ImageTk

import logging
logging.basicConfig()
logger = logging.getLogger("pressure")
logger.setLevel(logging.DEBUG)

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
        PressureDataType.PRESSURE_SINGLE_BYTE: 500
    }
}


def on_pressure_data(pressure_values: PressureValueList, timestamp: int):
    print(f"[{timestamp}]: {pressure_values[0]}")
    pass


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


def setup_window():
    global background_photo
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

    squares = []

    for position in square_positions:
        square = canvas.create_rectangle(
            position[0], position[1], position[0] + 30, position[1] + 30, fill='red')
        squares.append(square)

    def update_square_colors(opacities):
        for i, opacity in enumerate(opacities):
            red = int(opacity * 255)
            fill_color = f"#{red:02x}0000"
            canvas.itemconfig(squares[i], fill=fill_color)

    opacities = [0.5, 0.8, 1.0, 0.2,
                 0.4, 0.6, 0.9, 0.3,
                 0.7, 0.1, 0.5, 0.8,
                 1.0, 0.2, 0.4, 0.6]
    update_square_colors(opacities)


ukaton_mission.connection_event_dispatcher.add_event_listener(
    ConnectionEventType.CONNECTED, setup_window, True)

square_positions = [
    (50, 50), (100, 50), (150, 50), (200, 50),
    (50, 100), (100, 100), (150, 100), (200, 100),
    (50, 150), (100, 150), (150, 150), (200, 150),
    (50, 200), (100, 200), (150, 200), (200, 200)
]

window = tk.Tk()
window.mainloop()
