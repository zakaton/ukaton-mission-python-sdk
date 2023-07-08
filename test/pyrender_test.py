import trimesh
import pyrender
shoe_trimesh = trimesh.load(
    "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk/shoe.glb")
scene = pyrender.Scene.from_trimesh_scene(shoe_trimesh)
pyrender.Viewer(scene, use_raymond_lighting=True)
