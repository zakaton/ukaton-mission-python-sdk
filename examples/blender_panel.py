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

# TODO
# toggle sensor data UI
# display quaternion data
# rotate object UI
# active object or viewport UI


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
        p = scene.ukaton_mission_panel_properties

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(scene.ukaton_mission_panel_properties,
                    "connection_type", text="type", expand=True)

        if p.connection_type == 'BLE':
            layout.prop(p, "device_name", text="name")

        if p.connection_type == 'UDP':
            layout.prop(p, "ip_address", text="ip")

        layout.operator("object.toggle_connection_operator",
                        text=d.toggle_connection_text)

        if d.ukaton_mission is not None and d.ukaton_mission.is_connected:
            layout.operator("object.toggle_quaternion_data_operator",
                            text=d.toggle_quaternion_data_text)
            layout.label(text="quaternion:")
            row = layout.row()
            row.prop(p, "quaternion", text="")
            row.enabled = False


def run_toggle_connection(context):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(toggle_connection(context))
    loop.run_forever()


async def toggle_connection(context):
    scene = context.scene
    d = scene.ukaton_mission_panel_dict
    while not d.disconnect_flag.is_set():
        ukaton_mission = d.ukaton_mission
        if ukaton_mission is None:
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

    logger.info("disconnecting from device...")
    if ukaton_mission.is_connected:
        await ukaton_mission.disconnect()
        if not ukaton_mission.is_connected:
            logger.info("disconnected from device!")
            d.toggle_connection_text = "connect"
    logger.info("exiting toggle_connection")


def on_quaternion_data(quaternion, timestamp):
    logger.debug(f"[{timestamp}]: {quaternion}")


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
            if d.toggle_connection_thread:
                d.toggle_connection_thread = None
            d.ukaton_mission = None
        else:
            d.disconnect_flag.clear()
            d.toggle_connection_thread = threading.Thread(
                target=run_toggle_connection, args=(context,))
            d.toggle_connection_thread.daemon = True
            d.toggle_connection_thread.start()

        return {'FINISHED'}


def run_toggle_quaternion_data(context):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(toggle_quaternion_data(context))
    loop.run_forever()


async def toggle_quaternion_data(context):
    scene = context.scene
    d = scene.ukaton_mission_panel_dict
    quaternion_data_enabled = not d.quaternion_data_enabled

    logger.info(f"quaternion_data_enabled: {quaternion_data_enabled}")
    data_rate = 0
    if quaternion_data_enabled:
        data_rate = 20
        d.toggle_quaternion_data_text = "enabling..."
    else:
        d.toggle_quaternion_data_text = "disabling..."

    sensor_data_configurations = {
        SensorType.MOTION: {
            MotionDataType.QUATERNION: data_rate,
        }
    }
    await d.ukaton_mission.set_sensor_data_configurations(sensor_data_configurations)
    d.quaternion_data_enabled = quaternion_data_enabled
    d.toggle_quaternion_data_text = "disable" if d.quaternion_data_enabled else "enable"


class ToggleQuaternionDataOperator(bpy.types.Operator):
    """toggle quaternion data for a Ukaton Mission device"""
    bl_idname = "object.toggle_quaternion_data_operator"
    bl_label = "toggle quaternion data"

    def execute(self, context):
        scene = context.scene
        d = scene.ukaton_mission_panel_dict
        ukaton_mission = d.ukaton_mission

        if ukaton_mission is not None and ukaton_mission.is_connected:
            d.toggle_quaternion_data_thread = threading.Thread(
                target=run_toggle_quaternion_data, args=(context,))
            d.toggle_quaternion_data_thread.daemon = True
            d.toggle_quaternion_data_thread.start()

        return {'FINISHED'}


class UkatonMissionPanelProperties(PropertyGroup):
    connection_type: bpy.props.EnumProperty(
        items=connection_type_enum_items,
        default=ConnectionType.BLE.name
    )
    device_name: bpy.props.StringProperty(default="missionDevice")
    ip_address: bpy.props.StringProperty(default="192.168.1.30")
    quaternion: FloatVectorProperty(
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        subtype='QUATERNION'
    )


classes = [UkatonMissionPanel, ToggleConnectionOperator, ToggleQuaternionDataOperator,
           UkatonMissionPanelProperties]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ukaton_mission_panel_properties = bpy.props.PointerProperty(
        type=UkatonMissionPanelProperties)

    bpy.types.Scene.ukaton_mission_panel_dict = dotdict({
        "toggle_connection_thread": None,
        "disconnect_flag": threading.Event(),
        "ukaton_mission": None,
        "toggle_connection_text": "connect",
        "quaternion_data_enabled": False,
        "toggle_quaternion_data_text": "enable",
        "toggle_quaternion_data_thread": None
    })


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ukaton_mission_panel_properties
    del bpy.types.Scene.ukaton_mission_panel_dict


if __name__ == "__main__":
    register()
