import sys
sys.path.append(".")

from typing import Union

import logging
logging.basicConfig()
logger = logging.getLogger("3d")
logger.setLevel(logging.ERROR)

import trimesh
import pyrender
import numpy as np
import quaternion as Quaternion
import math

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, SensorDataConfigurations, DeviceType

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
    SensorType.MOTION: {
        MotionDataType.QUATERNION: 20
    }
}


def on_quaternion_data(quaternion: np.quaternion, timestamp: int):
    logger.debug(f"[{timestamp}]: {quaternion}")
    rotate_scene(quaternion)


ukaton_mission.motion_data_event_dispatcher.add_event_listener(
    MotionDataEventType.QUATERNION, on_quaternion_data)

did_save_initial_quaternions = False
initial_quaternions = []


rotate_quaternion_90_deg = trimesh.transformations.quaternion_from_euler(
    0, 0, -math.pi / 2)
# pyrender is x-right, z-up, and y-back


def rotate_scene(quaternion):
    global did_add_mesh
    if not did_add_mesh:
        return

    global did_save_initial_quaternions
    global initial_quaternions
    if not did_save_initial_quaternions and len(scene.mesh_nodes) > 0:
        for i, node in enumerate(scene.mesh_nodes):
            if hasattr(node, 'rotation'):
                x, y, z, w = node.rotation
                initial_quaternions.append([w, x, y, z])
        did_save_initial_quaternions = True

    if not did_save_initial_quaternions:
        return

    # quaternion_array: [w, x, y, z]
    quaternion_array = Quaternion.as_float_array(quaternion)
    w, x, y, z = quaternion_array
    quaternion_array = [w, x, -z, y]
    print(quaternion_array)
    viewer.render_lock.acquire()
    for i, node in enumerate(scene.mesh_nodes):
        if hasattr(node, 'rotation'):
            initial_quaternion = initial_quaternions[i]

            # trimesh.transformations.quaternion_multiply: [w, x, y, z]
            q = trimesh.transformations.quaternion_multiply(
                initial_quaternion, quaternion_array)
            w, x, y, z = trimesh.transformations.quaternion_multiply(
                q, rotate_quaternion_90_deg)
            # node.rotation: [w, x, y, z]
            node.rotation = [x, y, z, w]
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

model_names: dict[DeviceType, str] = {
    DeviceType.MOTION_MODULE: "motionModule",
    DeviceType.LEFT_INSOLE: "leftShoe",
    DeviceType.RIGHT_INSOLE: "rightShoe"
}


did_add_mesh = False


def add_mesh():
    global did_add_mesh
    if did_add_mesh:
        return
    model_trimesh = trimesh.load(
        f"/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk/assets/{model_names[ukaton_mission.device_type]}.gltf")
    model_scene = pyrender.Scene.from_trimesh_scene(model_trimesh)
    for i, node in enumerate(model_scene.mesh_nodes):
        scene.add_node(node)
    did_add_mesh = True


ukaton_mission.connection_event_dispatcher.add_event_listener(
    ConnectionEventType.CONNECTED, add_mesh, True)

scene = pyrender.Scene()
# change __init__ in viewer.py so it returns before it starts the viewer (after self._is_active = True), so we can access the viewer object. auto_start= and run_in_thread don't work, and this is the only way to make the viewer object accessible for rotate_scene
viewer = pyrender.Viewer(
    scene, use_raymond_lighting=True)
viewer._init_and_start_app()
