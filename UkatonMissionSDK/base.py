import abc
import time
from UkatonMissionSDK.utils import *
from UkatonMissionSDK.enumerations import *
from UkatonMissionSDK.parsers import *
import numpy as np
import quaternion
from typing import Union
import logging

logging.basicConfig()
logger = logging.getLogger("BaseUkatonMission")
logger.setLevel(logging.ERROR)


class BaseUkatonMission(abc.ABC):
    number_of_pressure_sensors = 16

    def __init__(self):
        super().__init__()
        self.is_connected: bool = False
        self.connection_event_dispatcher: EventDispatcher = EventDispatcher(
            ConnectionEventType)
        self.motion_data_event_dispatcher: EventDispatcher = EventDispatcher(
            MotionDataEventType)
        self.pressure_data_event_dispatcher: EventDispatcher = EventDispatcher(
            PressureDataEventType)

        self.device_type: DeviceType = DeviceType.MOTION_MODULE
        self.device_name: str = ""
        self.battery_level: int = 0

        self.motion_data: dict[MotionDataType, Union[Vector3, np.quaternion]] = {
            MotionDataType.ACCELERATION: Vector3(),
            MotionDataType.GRAVITY: Vector3(),
            MotionDataType.LINEAR_ACCELERATION: Vector3(),
            MotionDataType.ROTATION_RATE: Vector3(),
            MotionDataType.MAGNETOMETER: Vector3(),
            MotionDataType.QUATERNION: np.quaternion(),
            MotionDataType.EULER: Vector3()
        }
        self.pressure_data: dict[PressureDataType, Union[PressureValueList, float, Vector2]] = {
            PressureDataType.PRESSURE_SINGLE_BYTE: PressureValueList(self.__class__.number_of_pressure_sensors, PressureDataType.PRESSURE_SINGLE_BYTE),
            PressureDataType.PRESSURE_DOUBLE_BYTE: PressureValueList(self.__class__.number_of_pressure_sensors, PressureDataType.PRESSURE_SINGLE_BYTE),
            PressureDataType.CENTER_OF_MASS: Vector2(),
            PressureDataType.MASS: 0,
            PressureDataType.HEEL_TO_TOE: Vector2(),
        }
        self.pressure_values: Optional[PressureValueList] = None
        self._last_time_received_sensor_data: int = 0
        self._last_raw_sensor_data_timestamp: int = 0
        self._sensor_data_timestamp_offset: int = 0

    @property
    def is_insole(self) -> bool:
        return self.device_type is not DeviceType.MOTION_MODULE

    @property
    def insole_side(self) -> InsoleSide:
        return InsoleSide.RIGHT if self.device_type is DeviceType.RIGHT_INSOLE else InsoleSide.LEFT

    def _connection_handler(self):
        self.is_connected = True
        self.connection_event_dispatcher.dispatch(
            ConnectionEventType.CONNECTED)

    def _disconnection_handler(self, *args):
        self.is_connected = False
        self.connection_event_dispatcher.dispatch(
            ConnectionEventType.DISCONNECTED)

    @abc.abstractmethod
    async def connect(self, device_identifier: str):
        raise NotImplementedError()

    @abc.abstractmethod
    async def disconnect(self):
        raise NotImplementedError()

    def parse_device_type_data(self, data: bytearray, byte_offset: int = 0) -> int:
        self.device_type = DeviceType(data[byte_offset])
        byte_offset += 1
        logger.debug(f"device_type: {self.device_type.name}")
        return byte_offset

    def parse_battery_level_data(self, data: bytearray, byte_offset: int = 0) -> int:
        self.battery_level = data[byte_offset]
        byte_offset += 1
        logger.debug(f"battery_level: {self.battery_level}")
        return byte_offset

    async def set_sensor_data_configurations(self, sensor_data_configurations: SensorDataConfigurations):
        serialized_sensor_data_configurations = serialize_sensor_data_configurations(
            sensor_data_configurations)
        await self._send_sensor_data_configurations(
            serialized_sensor_data_configurations)

    @abc.abstractmethod
    async def _send_sensor_data_configurations(self, serialized_sensor_data_configurations: bytearray):
        raise NotImplementedError()

    def parse_sensor_data(self, data: bytearray, byte_offset: int = 0) -> int:
        self._last_time_received_sensor_data = time.time()
        raw_timestamp = get_uint_16(data, byte_offset)
        if raw_timestamp < self._last_raw_sensor_data_timestamp:
            self._sensor_data_timestamp_offset += 2 ** 16
        self._last_raw_sensor_data_timestamp = raw_timestamp
        timestamp = raw_timestamp + self._sensor_data_timestamp_offset
        byte_offset += 2
        logger.debug(f"timestamp: {timestamp}")

        data_len = len(data)
        while byte_offset < data_len:
            sensor_type = SensorType(data[byte_offset])
            byte_offset += 1
            logger.debug(f"sensor_type: {sensor_type}")
            byte_offset = self._parse_sensor_data_type(
                data, byte_offset, timestamp, sensor_type)

        return byte_offset

    def _parse_sensor_data_type(self, data: bytearray, byte_offset: int, timestamp: int, sensor_type: SensorType) -> int:
        data_size = data[byte_offset]
        byte_offset += 1
        logger.debug(f"data_size: {data_size}")

        final_byte_offset = byte_offset + data_size

        match sensor_type:
            case SensorType.MOTION:
                byte_offset = self._parse_motion_data(
                    data, byte_offset, final_byte_offset, timestamp)
            case SensorType.PRESSURE:
                byte_offset = self._parse_pressure_data(
                    data, byte_offset, final_byte_offset, timestamp)
            case _:
                logger.debug(f'undefined sensor_type "{sensor_type}')

        return byte_offset

    def _parse_motion_data(self, data: bytearray, byte_offset: int, final_byte_offset: int, timestamp: int):
        while byte_offset < final_byte_offset:
            motion_sensor_data_type = MotionDataType(data[byte_offset])
            byte_offset += 1
            logger.debug(f"motion_sensor_data_type: {motion_sensor_data_type}")

            scalar = motion_data_scalars[motion_sensor_data_type]

            match motion_sensor_data_type:
                case MotionDataType.ACCELERATION | MotionDataType.GRAVITY | MotionDataType.LINEAR_ACCELERATION | MotionDataType.MAGNETOMETER:
                    vector = parse_motion_vector(
                        data, byte_offset, scalar, self.device_type)
                    byte_offset += 6
                    logger.debug(f"vector: {vector}")
                    self.motion_data[motion_sensor_data_type] = vector
                    self.motion_data_event_dispatcher.dispatch(
                        MotionDataEventType(motion_sensor_data_type), vector, timestamp)
                case MotionDataType.ROTATION_RATE:
                    euler = parse_motion_euler(
                        data, byte_offset, scalar, self.device_type)
                    byte_offset += 6
                    logger.debug(f"euler: {euler}")
                    self.motion_data[motion_sensor_data_type] = euler
                    self.motion_data_event_dispatcher.dispatch(
                        MotionDataEventType(motion_sensor_data_type), euler, timestamp)
                case MotionDataType.QUATERNION:
                    quat = parse_motion_quaternion(
                        data, byte_offset, scalar, self.device_type)
                    byte_offset += 8
                    if quat.norm() > 0:
                        self.motion_data[motion_sensor_data_type] = quat
                        logger.debug(f"quat: {quat}")
                        self.motion_data_event_dispatcher.dispatch(
                            MotionDataEventType(motion_sensor_data_type), quat, timestamp)

                        euler = quaternion.as_euler_angles(quat)
                        self.motion_data[MotionDataType.EULER] = euler
                        logger.debug(f"euler: {euler}")
                        self.motion_data_event_dispatcher.dispatch(
                            MotionDataEventType.EULER, euler, timestamp)

                case _:
                    logger.debug(
                        f'undefined motion_sensor_data_type: {motion_sensor_data_type}')

        return byte_offset

    def _parse_pressure_data(self, data: bytearray, byte_offset: int, final_byte_offset: int, timestamp: int):
        while byte_offset < final_byte_offset:
            pressure_sensor_data_type = PressureDataType(data[byte_offset])
            byte_offset += 1
            logger.debug(
                f'pressure_sensor_data_type: {pressure_sensor_data_type}')

            scalar = pressure_data_scalars[pressure_sensor_data_type]

            match pressure_sensor_data_type:
                case PressureDataType.PRESSURE_SINGLE_BYTE | PressureDataType.PRESSURE_DOUBLE_BYTE:
                    pressure_values: PressureValueList = PressureValueList(
                        self.__class__.number_of_pressure_sensors, pressure_sensor_data_type)
                    for i in range(self.__class__.number_of_pressure_sensors):
                        value = 0
                        if pressure_sensor_data_type == PressureDataType.PRESSURE_SINGLE_BYTE:
                            value = data[byte_offset]
                            byte_offset += 1
                        else:
                            value = get_uint_16(data, byte_offset)
                            byte_offset += 2
                        (x, y) = get_pressure_position(i, self.device_type)
                        pressure_values[i] = PressureValue(x, y, value)

                    pressure_values.update()
                    logger.debug(f"pressure_values: {pressure_values}")
                    self.pressure_values = pressure_values
                    self.pressure_data[pressure_sensor_data_type] = pressure_values
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.PRESSURE, pressure_values, timestamp)
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.CENTER_OF_MASS, pressure_values.center_of_mass, timestamp)
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.MASS, pressure_values.mass, timestamp)
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.HEEL_TO_TOE, pressure_values.heel_to_toe, timestamp)

                case PressureDataType.CENTER_OF_MASS:
                    center_of_mass = Vector2(get_float_32(
                        data, byte_offset), get_float_32(data, byte_offset + 4))
                    self.pressure_data[pressure_sensor_data_type] = center_of_mass
                    logger.debug(f"center_of_mass: {center_of_mass}")
                    byte_offset += 4 * 2
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.CENTER_OF_MASS, center_of_mass, timestamp)
                    heel_to_toe = center_of_mass.y
                    self.pressure_data[PressureDataType.HEEL_TO_TOE] = heel_to_toe
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.HEEL_TO_TOE, heel_to_toe, timestamp)
                case PressureDataType.MASS:
                    mass = get_uint_32(data, byte_offset) * scalar
                    logger.debug(f"mass: {mass}")
                    self.pressure_data[pressure_sensor_data_type] = mass
                    byte_offset += 4
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.MASS, mass, timestamp)
                case PressureDataType.HEEL_TO_TOE:
                    heel_to_toe = get_float_64(data, byte_offset)
                    logger.debug(f"heel_to_toe: {heel_to_toe}")
                    self.pressure_data[pressure_sensor_data_type] = heel_to_toe
                    byte_offset += 8
                    self.pressure_data_event_dispatcher.dispatch(
                        PressureDataEventType.HEEL_TO_TOE, heel_to_toe, timestamp)
                case _:
                    logger.debug(
                        f'undefined pressure_sensor_data_type: {pressure_sensor_data_type}')

        return byte_offset

    async def vibrate_waveform(self, waveform: list[int]):
        vibration = bytearray([VibrationType.WAVEFORM, *waveform])
        await self._send_vibration(vibration)

    async def vibrate_sequence(self, sequence: list[int]):
        is_sequence_odd = len(sequence) % 2 == 1
        if is_sequence_odd:
            sequence = sequence[0:-1]
        sequence = list(
            map(self._format_vibration_sequence, enumerate(sequence)))
        vibration = bytearray([VibrationType.SEQUENCE, *sequence])
        await self._send_vibration(vibration)

    def _format_vibration_sequence(self, pair):
        index, value = pair
        is_index_odd = index % 2 == 1
        if is_index_odd:
            value = math.floor(value / 10)
        return value

    @abc.abstractmethod
    def _send_vibration(self, vibration: bytearray):
        raise NotImplementedError()


class BaseUkatonMissions(abc.ABC):
    UkatonMission: type[BaseUkatonMission]

    class MissionsPressureData:
        sum: float = 0
        mass: dict[InsoleSide, float] = {
            InsoleSide.LEFT: 0, InsoleSide.RIGHT: 0}
        center_of_mass: Vector2 = Vector2()

    def __init__(self):
        super().__init__()

        self.pressure_data = self.MissionsPressureData()
        self.pressure_data_event_dispatcher: EventDispatcher = EventDispatcher(
            PressureDataEventType)

        self.ukaton_missions: dict[InsoleSide, BaseUkatonMission] = {}
        for side in InsoleSide:
            self.ukaton_missions[side] = self.__class__.UkatonMission()

        for ukaton_mission in self.ukaton_missions.values():
            ukaton_mission.pressure_data_event_dispatcher.add_event_listener(
                PressureDataEventType.PRESSURE, self.update_pressure_data)

    def update_pressure_data(self, pressure_values: PressureValueList, timestamp: int):
        pressure_data = self.MissionsPressureData()
        ukaton_missions = {side: ukaton_mission for side, ukaton_mission in self.ukaton_missions.items(
        ) if ukaton_mission.pressure_values is not None}
        for ukaton_mission in ukaton_missions.values():
            pressure_data.sum += ukaton_mission.pressure_values.sum
        if pressure_data.sum > 0:
            for side, ukaton_mission in self.ukaton_missions.items():
                pressure_data.mass[side] = ukaton_mission.pressure_values.sum / \
                    pressure_data.sum
            pressure_data.center_of_mass.x = pressure_data.mass[InsoleSide.RIGHT]

            pressure_data.center_of_mass.y = 0
            for side, ukaton_mission in self.ukaton_missions.items():
                pressure_data.center_of_mass.y += ukaton_missions[side].pressure_values.center_of_mass.y * \
                    pressure_data.mass[side]
            self.pressure_data = pressure_data
            self.pressure_data_event_dispatcher.dispatch(
                PressureDataEventType.PRESSURE, pressure_data, timestamp)

    def replace_insole(self, ukaton_mission: BaseUkatonMission):
        if ukaton_mission.is_insole and self.ukaton_missions[ukaton_mission.insole_side] is not ukaton_mission:
            self.ukaton_missions[ukaton_mission.insole_side].pressure_data_event_dispatcher.remove_event_listener(
                PressureDataEventType.PRESSURE, self.update_pressure_data)
            ukaton_mission.pressure_data_event_dispatcher.add_event_listener(
                PressureDataEventType.PRESSURE, self.update_pressure_data)
            self.ukaton_missions[ukaton_mission.insole_side] = ukaton_mission
