import sys
sys.path.append(".")

from typing import Union

import logging
logging.basicConfig()
logger = logging.getLogger("3d")
logger.setLevel(logging.DEBUG)

import trimesh
import pyrender
import numpy as np
import quaternion as Quaternion

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, SensorDataConfigurations

use_ble = True
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
    SensorType.MOTION: {
        MotionDataType.QUATERNION: 20
    }
}


def on_quaternion_data(quaternion: np.quaternion, timestamp: int):
    # print(f"[{timestamp}]: {quaternion}")
    rotate_scene(quaternion)


ukaton_mission.motion_data_event_dispatcher.add_event_listener(
    MotionDataEventType.QUATERNION, on_quaternion_data)


def rotate_scene(quaternion):
    quaternion_array = Quaternion.as_float_array(quaternion)
    print(f"before: {quaternion}, after: {quaternion_array}")
    viewer.render_lock.acquire()
    for node in scene.nodes:
        if hasattr(node, 'rotation'):
            node.rotation = quaternion_array
    viewer.render_lock.release()


async def main():
    logger.debug("connecting to device...")
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


shoe_trimesh = trimesh.load(
    "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk/shoe.glb")
scene = pyrender.Scene.from_trimesh_scene(shoe_trimesh)
# change __init__ in viewer.py so it returns before it starts the viewer (after self._is_active = True), so we can access the viewer object. auto_start= and run_in_thread don't work, and this is the only way to make the viewer object accessible for rotate_scene
viewer = pyrender.Viewer(
    scene, use_raymond_lighting=True)
viewer._init_and_start_app()
