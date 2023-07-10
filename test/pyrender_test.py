import trimesh
import pyrender
import numpy as np
import threading
import asyncio

viewer = None
did_save_initial_quaternions = False
initial_quaternions = []


async def rotate_object():
    global did_save_initial_quaternions
    global initial_quaternions
    i = 0
    while True:
        if viewer is None:
            continue

        if not did_save_initial_quaternions:
            for j, node in enumerate(scene.mesh_nodes):
                if hasattr(node, 'rotation'):
                    x, y, z, w = node.rotation
                    initial_quaternions.append([w, x, y, z])
            did_save_initial_quaternions = True
        q = trimesh.transformations.quaternion_from_euler(i, 0, 0)
        # w, x, y, z
        translation = [0, i, 0]
        # print(translation)

        viewer.render_lock.acquire()
        # print(viewer._camera_node.translation)
        for j, node in enumerate(scene.mesh_nodes):
            if hasattr(node, 'rotation'):
                initial_quaternion = initial_quaternions[j]
                _q = trimesh.transformations.quaternion_multiply(
                    initial_quaternion, q)
                w, x, y, z = _q
                print(f"w: {w}, x: {x}, y: {y}, z: {z}")
                node.rotation = [x, y, z, w]
                # print(node.rotation)
                pass
        for j, node in enumerate(scene.mesh_nodes):
            if hasattr(node, 'translation'):
                # node.translation = translation
                # print(node.translation)
                pass
        viewer.render_lock.release()
        i += 0.01
        await asyncio.sleep(0.1)


def run_rotate_object():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(rotate_object())
    loop.run_forever()


rotate_object_thread = threading.Thread(target=run_rotate_object)
rotate_object_thread.daemon = True
rotate_object_thread.start()

loaded_trimesh = trimesh.load(
    "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk/assets/leftShoe.gltf")
scene = pyrender.Scene.from_trimesh_scene(loaded_trimesh)
viewer = pyrender.Viewer(scene, use_raymond_lighting=True)
viewer._init_and_start_app()
