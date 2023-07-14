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

        d = bpy.types.Scene.ukaton_mission_panel_dict

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(scene.ukaton_mission_panel_properties,
                    "connection_type", text="type", expand=True)

        if scene.ukaton_mission_panel_properties.connection_type == 'BLE':
            layout.prop(scene.ukaton_mission_panel_properties,
                        "device_name", text="name")

        if scene.ukaton_mission_panel_properties.connection_type == 'UDP':
            layout.prop(scene.ukaton_mission_panel_properties,
                        "ip_address", text="ip")

        toggle_connection_text = "connect"
        if d.ukaton_mission is not None:
            if d.ukaton_mission.is_connecting:
                toggle_connection_text = "connecting..."
            elif d.ukaton_mission.is_connected:
                toggle_connection_text = "disconnect"
        layout.operator("object.toggle_connection_operator",
                        text=toggle_connection_text)

        layout.label(text="quaternion:")
        row = layout.row()
        row.prop(scene.ukaton_mission_panel_properties, "quaternion", text="")
        row.enabled = False


def run_connect_to_device(context):
    print("run_connect_to_device")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(connect_to_device(context))
    loop.run_forever()


async def connect_to_device(context):
    scene = context.scene
    d = bpy.types.Scene.ukaton_mission_panel_dict
    print(f"d.disconnect_flag.is_set(): {d.disconnect_flag.is_set()}")
    while not d.disconnect_flag.is_set():
        properties = scene.ukaton_mission_panel_properties
        print(f"properties: {properties}")
        connection_type = getattr(
            ConnectionType, properties.connection_type)
        print(f"connection_type: {connection_type}")
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
            logger.info(
                "attempting to connect to ukaton mission device...")
            await ukaton_mission.connect(device_identifier)

        logger.info("disconnecting from device...")
        if ukaton_mission.is_connected:
            await ukaton_mission.disconnect()


class ToggleConnectionOperator(bpy.types.Operator):
    """toggle connection to a Ukaton Mission device via bluetooth or udp"""
    bl_idname = "object.toggle_connection_operator"
    bl_label = "toggle connection"

    def execute(self, context):
        d = bpy.types.Scene.ukaton_mission_panel_dict
        ukaton_mission = d.ukaton_mission
        print(ukaton_mission is not None)

        if ukaton_mission is not None:
            d.disconnect_flag.set()
            if d.connect_to_device_thread:
                d.connect_to_device_thread.join()
                d.connect_to_device_thread = None
            d.ukaton_mission = None
        else:
            d.disconnect_flag.clear()
            d.connect_to_device_thread = threading.Thread(
                target=run_connect_to_device, args=(context,))
            d.connect_to_device_thread.start()

        return {'FINISHED'}


class UkatonMissionPanelProperties(PropertyGroup):
    connection_type: bpy.props.EnumProperty(
        items=connection_type_enum_items,
        default=ConnectionType.BLE.name
    )
    device_name: bpy.props.StringProperty(default="missionDevice")
    ip_address: bpy.props.StringProperty(default="0.0.0.0")
    quaternion: FloatVectorProperty(
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        subtype='QUATERNION'
    )


classes = [UkatonMissionPanel, ToggleConnectionOperator,
           UkatonMissionPanelProperties]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ukaton_mission_panel_properties = bpy.props.PointerProperty(
        type=UkatonMissionPanelProperties)

    bpy.types.Scene.ukaton_mission_panel_dict = dotdict({
        "connect_to_device_thread": None,
        "disconnect_flag": threading.Event(),
        "ukaton_mission": None
    })


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ukaton_mission_panel_properties
    del bpy.types.Scene.ukaton_mission_panel_dict


if __name__ == "__main__":
    register()
