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
from bpy.types import Panel, PropertyGroup
from bpy.props import EnumProperty, StringProperty, FloatVectorProperty

import logging
logging.basicConfig()
logger = logging.getLogger("ukaton_mission_panel")
logger.setLevel(logging.DEBUG)

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


def on_sensor_data(sensor, timestamp):
    logger.debug(f"[{timestamp}]: {sensor}")


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
            MotionDataEventType.QUATERNION, on_sensor_data)
        logger.info(
            "attempting to connect to ukaton mission device...")
        d.toggle_connection_text = "connecting..."
        await ukaton_mission.connect(device_identifier)
        if ukaton_mission.is_connected:
            logger.info(f"connected to device!")
            d.toggle_connection_text = "disconnect"


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
    # asyncio.run(connection_loop(context))


class ToggleConnectionOperator(bpy.types.Operator):
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


class ToggleSensorDataOperator(bpy.types.Operator):
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
                data_rate = 20
            else:
                d.toggle_sensor_data_text = "disabling sensor data..."
            d.sensor_data_configurations[SensorType.MOTION][MotionDataType.QUATERNION] = data_rate
            d.should_set_sensor_data_configurations = True

        return {'FINISHED'}


class UkatonMissionPanelProperties(PropertyGroup):
    connection_type: bpy.props.EnumProperty(
        items=connection_type_enum_items,
        default=ConnectionType.BLE.name
    )
    device_name: bpy.props.StringProperty(default="missionDevice")
    ip_address: bpy.props.StringProperty(default="192.168.1.30")


classes = [UkatonMissionPanel, ToggleConnectionOperator, ToggleSensorDataOperator,
           UkatonMissionPanelProperties]


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
        "should_set_sensor_data_configurations": False
    })


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ukaton_mission_panel_properties
    del bpy.types.Scene.ukaton_mission_panel_dict


if __name__ == "__main__":
    register()
