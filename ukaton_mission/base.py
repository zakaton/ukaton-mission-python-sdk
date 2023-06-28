import abc
from ukaton_mission.utils import *
from ukaton_mission.enumerations import *
from ukaton_mission.parsers import *


class BaseUkatonMission(abc.ABC):
    def __init__(self):
        self.event_dispatcher = EventDispatcher(EventType)
        self.device_type = DeviceType.MOTION_MODULE
        self.device_name = ""
        self.battery_level = 0
        self.pressure_data: dict[PressureDataType, object] = {}
        self.motion_data: dict[MotionDataType, object] = {}

    @abc.abstractmethod
    def connect(identifier: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect():
        raise NotImplementedError()

    @abc.abstractmethod
    def set_sensor_data_configuration(sensor_data_configuration: dict[str, dict[str, int]]):
        raise NotImplementedError()

    @abc.abstractmethod
    def vibrate_waveform(waveform: list[int]):
        raise NotImplementedError()

    @abc.abstractmethod
    def vibrate_sequence(sequence: list[int]):
        raise NotImplementedError()


class BaseUkatonMissions(abc.ABC):
    pass
