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

from UkatonMissionSDK import BLEUkatonMission, UDPUkatonMission, ConnectionEventType, SensorType, MotionDataType, PressureDataType, BLEUkatonMissions, MotionDataEventType, SensorDataConfigurations, ConnectionType

connection_type_enum_items = [(connection_type.name, connection_type.name.lower(
), "") for connection_type in ConnectionType]

# TODO
# connection UI
# toggle sensor data UI
# display quaternion data
# rotate object UI
# active object or viewport UI


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

        layout.operator("object.connect_operator")

        layout.label(text="quaternion:")
        row = layout.row()
        row.prop(scene.ukaton_mission_panel_properties, "quaternion", text="")
        row.enabled = False


class ConnectOperator(bpy.types.Operator):
    bl_idname = "object.connect_operator"
    bl_label = "connect"

    def execute(self, context):
        if hasattr(bpy.types.Scene, "ukaton_mission"):
            bpy.types.Scene.ukaton_mission.disconnect()

        properties = context.scene.ukaton_mission_panel_properties
        connection_type = getattr(ConnectionType, properties.connection_type)
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
            bpy.types.Scene.ukaton_mission = ukaton_mission
            logger.info("attempting to connect to ukaton mission device...")
            # FILL - event listeners
            # FILL - connect
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


classes = [UkatonMissionPanel, ConnectOperator, UkatonMissionPanelProperties]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ukaton_mission_panel_properties = bpy.props.PointerProperty(
        type=UkatonMissionPanelProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ukaton_mission_panel_properties
    if hasattr(bpy.types.Scene, "ukaton_mission"):
        bpy.types.Scene.ukaton_mission.disconnect()
        del bpy.types.Scene.ukaton_mission


if __name__ == "__main__":
    register()
