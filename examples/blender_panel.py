import sys
local_module_paths = [
    "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk",
    "/usr/local/lib/python3.10/site-packages"
]
for local_module_path in local_module_paths:
    if local_module_path not in sys.path:
        sys.path.append(local_module_path)

bl_info = {
    # required
    'name': 'Ukaton Mission Addon',
    'blender': (3, 6, 0),
    'category': 'Object',
    # optional
    'version': (1, 0, 0),
    'author': 'Zack Qattan x ChatGPT',
    'description': 'Rotate objects using a Ukaton Mission device',
}

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, FloatVectorProperty
import mathutils
import math
import quaternion as Quaternion

import logging
logging.basicConfig()
logger = logging.getLogger("ukaton_mission_panel")
logger.setLevel(logging.INFO)

import threading
import asyncio
from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, SensorDataConfigurations, ConnectionType

connection_type_enum_items = [(connection_type.name, connection_type.name.lower(
), "") for connection_type in ConnectionType]


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class UkatonMissionPanel(Panel):
    """Creates a Ukaton Mission Panel in the 3D view"""
    bl_label = "Ukaton Mission"
    bl_idname = "VIEW_3D_PT_ukaton_mission_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ukaton"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        d = scene.ukaton_mission_panel_dict
        ukaton_mission = d.ukaton_mission
        is_connected = ukaton_mission is not None and ukaton_mission.is_connected
        p = scene.ukaton_mission_panel_properties

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.prop(scene.ukaton_mission_panel_properties,
                 "connection_type", text="type", expand=True)
        if is_connected:
            row.enabled = False

        row = layout.row()
        if p.connection_type == 'BLE':
            row.prop(p, "device_name", text="name")
        if p.connection_type == 'UDP':
            row.prop(p, "ip_address", text="ip")
        if is_connected:
            row.enabled = False

        if is_connected:
            row = layout.row()
            row.label(text=f"device type: {ukaton_mission.device_type.name}")

        layout.operator("object.toggle_connection_operator",
                        text=d.toggle_connection_text)

        if d.ukaton_mission is not None and d.ukaton_mission.is_connected:
            layout.operator("object.toggle_sensor_data_operator",
                            text=d.toggle_sensor_data_text)
            layout.operator("object.toggle_object_orbit_operator",
                            text=d.toggle_object_orbit_text)
            layout.operator("object.toggle_viewport_orbit_operator",
                            text=d.toggle_viewport_orbit_text)


def update_euler_offset(context):
    d = context.scene.ukaton_mission_panel_dict
    euler = d.latest_quaternion.to_euler("ZYX")
    euler.x = euler.y = 0
    euler.z *= -1
    d.euler_offset = euler


def on_quaternion_data(quaternion, timestamp):
    logger.debug(f"[{timestamp}]: {quaternion}")
    on_quaternion(quaternion)


def on_quaternion(quaternion):
    quaternion = convert_quaternion_from_webgl_to_blender(quaternion)
    d = bpy.context.scene.ukaton_mission_panel_dict
    d.latest_quaternion = quaternion
    quaternion.rotate(d.euler_offset)
    logger.debug(f"quaternion: {quaternion}")

    if d.should_orbit_object:
        d.object_to_orbit.rotation_quaternion = quaternion

    if d.should_orbit_viewport:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces.active
                    v3d = space.region_3d
                    v3d.view_rotation = quaternion
                    break


# I used chatGPT to fix the quaternion
webgl_to_blender_matrix = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')


def convert_quaternion_from_webgl_to_blender(quaternion):
    quaternion_array = Quaternion.as_float_array(quaternion)
    w, x, y, z = quaternion_array
    quaternion = mathutils.Quaternion((w, x, y, z))
    matrix = quaternion.to_matrix().to_4x4()
    matrix = webgl_to_blender_matrix @ matrix
    quaternion = matrix.to_quaternion()
    return quaternion


async def connection_loop(context):
    scene = context.scene
    d = scene.ukaton_mission_panel_dict
    while not d.disconnect_flag.is_set():
        ukaton_mission = d.ukaton_mission
        if ukaton_mission is None:
            await connect_to_device(context)
        else:
            if d.should_set_sensor_data_configurations:
                s = "enable" if d.is_sensor_data_enabled else "disable"
                logger.info(f"about to {s} sensor data...")
                await d.ukaton_mission.set_sensor_data_configurations(d.sensor_data_configurations)
                d.toggle_sensor_data_text = "disable sensor data" if d.is_sensor_data_enabled else "enable sensor data"
                logger.info(f"did {s} sensor data")
                d.should_set_sensor_data_configurations = False
            elif d.is_sensor_data_enabled:
                # without this it doesn't work with BLEUkatonMission
                await asyncio.sleep(0.1)

    ukaton_mission = d.ukaton_mission
    if ukaton_mission.is_connected:
        await disconnect_from_device(context)
    logger.info("exiting toggle_connection")


async def connect_to_device(context):
    scene = context.scene
    d = scene.ukaton_mission_panel_dict
    properties = scene.ukaton_mission_panel_properties
    connection_type = getattr(
        ConnectionType, properties.connection_type)
    ukaton_mission = None
    device_identifier = None
    match connection_type:
        case ConnectionType.BLE:
            ukaton_mission = BLEUkatonMission()
            device_identifier = properties.device_name
        case ConnectionType.UDP:
            ukaton_mission = UDPUkatonMission()
            device_identifier = properties.ip_address
    if ukaton_mission is not None:
        d.ukaton_mission = ukaton_mission
        ukaton_mission.motion_data_event_dispatcher.add_event_listener(
            MotionDataEventType.QUATERNION, on_quaternion_data)
        logger.info(
            "attempting to connect to ukaton mission device...")
        d.toggle_connection_text = "connecting..."
        await ukaton_mission.connect(device_identifier)
        if ukaton_mission.is_connected:
            logger.info(f"connected to device!")
            d.toggle_connection_text = "disconnect"
        else:
            logger.info(f"couldn't connect to device")
            del d.ukaton_mission
            d.toggle_connection_text = "connect"


async def disconnect_from_device(context):
    logger.info("disconnecting from device...")
    scene = context.scene
    d = scene.ukaton_mission_panel_dict
    ukaton_mission = d.ukaton_mission
    await ukaton_mission.disconnect()
    if not ukaton_mission.is_connected:
        logger.info("disconnected from device!")
        d.toggle_connection_text = "connect"
    del d.ukaton_mission


def run_connection_loop(context):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(connection_loop(context))
    loop.run_forever()


class ToggleConnectionOperator(Operator):
    """toggle connection to a Ukaton Mission device via bluetooth or udp"""
    bl_idname = "object.toggle_connection_operator"
    bl_label = "toggle connection"

    def execute(self, context):
        scene = context.scene
        d = scene.ukaton_mission_panel_dict
        ukaton_mission = d.ukaton_mission

        if ukaton_mission is not None:
            d.disconnect_flag.set()
            if d.connection_loop_thread:
                d.connection_loop_thread = None
        else:
            d.disconnect_flag.clear()
            d.connection_loop_thread = threading.Thread(
                target=run_connection_loop, args=(context,))
            # d.connection_loop_thread.daemon = True
            d.connection_loop_thread.start()

        return {'FINISHED'}


class ToggleSensorDataOperator(Operator):
    """toggle sensor data for a Ukaton Mission device"""
    bl_idname = "object.toggle_sensor_data_operator"
    bl_label = "toggle sensor data"

    def execute(self, context):
        scene = context.scene
        d = scene.ukaton_mission_panel_dict
        ukaton_mission = d.ukaton_mission

        if ukaton_mission is not None and ukaton_mission.is_connected:
            d.is_sensor_data_enabled = not d.is_sensor_data_enabled
            data_rate = 0
            if d.is_sensor_data_enabled:
                d.toggle_sensor_data_text = "enabling sensor data..."
                data_rate = 40
            else:
                d.toggle_sensor_data_text = "disabling sensor data..."
            d.sensor_data_configurations[SensorType.MOTION][MotionDataType.QUATERNION] = data_rate
            d.should_set_sensor_data_configurations = True

        return {'FINISHED'}


class ToggleObjectOrbitOperator(Operator):
    """Orbit the active object"""
    bl_idname = "object.toggle_object_orbit_operator"
    bl_label = "Toggle Object Orbit"

    def execute(self, context):
        scene = context.scene
        d = scene.ukaton_mission_panel_dict
        should_orbit_object = not d.should_orbit_object
        active_object = context.view_layer.objects.active
        if should_orbit_object and active_object is not None:
            d.object_to_orbit = active_object
            active_object.rotation_mode = 'QUATERNION'
            update_euler_offset(context)
        else:
            d.object_to_orbit = None
            should_orbit_object = False
        d.should_orbit_object = should_orbit_object
        d.toggle_object_orbit_text = "stop orbiting object" if d.should_orbit_object else "orbit object"
        return {'FINISHED'}


class ToggleViewportOrbitOperator(Operator):
    """Orbit the viewport"""
    bl_idname = "object.toggle_viewport_orbit_operator"
    bl_label = "Toggle Viewport Orbit"

    def execute(self, context):
        scene = context.scene
        d = scene.ukaton_mission_panel_dict
        d.should_orbit_viewport = not d.should_orbit_viewport
        if d.should_orbit_viewport:
            update_euler_offset(context)
        d.toggle_viewport_orbit_text = "stop orbiting viewport" if d.should_orbit_viewport else "orbit viewport"
        return {'FINISHED'}


class UkatonMissionPanelProperties(PropertyGroup):
    connection_type: bpy.props.EnumProperty(
        items=connection_type_enum_items,
        default=ConnectionType.BLE.name
    )
    device_name: bpy.props.StringProperty(default="missionDevice")
    ip_address: bpy.props.StringProperty(default="192.168.1.30")


classes = [
    UkatonMissionPanel,
    ToggleConnectionOperator,
    ToggleSensorDataOperator,
    ToggleObjectOrbitOperator,
    ToggleViewportOrbitOperator,
    UkatonMissionPanelProperties
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ukaton_mission_panel_properties = bpy.props.PointerProperty(
        type=UkatonMissionPanelProperties)

    bpy.types.Scene.ukaton_mission_panel_dict = dotdict({
        "ukaton_mission": None,
        "toggle_connection_text": "connect",
        "connection_loop_thread": None,
        "disconnect_flag": threading.Event(),
        "is_sensor_data_enabled": False,
        "toggle_sensor_data_text": "enable sensor data",
        "sensor_data_configurations": {
            SensorType.MOTION: {
                MotionDataType.QUATERNION: 0,
            }
        },
        "toggle_object_orbit_text": "orbit object",
        "toggle_viewport_orbit_text": "orbit viewport",
        "should_set_sensor_data_configurations": False,
        "euler_offset": mathutils.Euler(),
        "latest_quaternion": mathutils.Quaternion(),
        "should_orbit_object": False,
        "object_to_orbit": None,
        "should_orbit_viewport": False,
    })


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ukaton_mission_panel_properties
    del bpy.types.Scene.ukaton_mission_panel_dict


if __name__ == "__main__":
    register()
