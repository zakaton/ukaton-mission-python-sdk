import abc
from ukaton_mission.utils import *
from ukaton_mission.enumerations import *
from ukaton_mission.parsers import *


class BaseUkatonMission(abc.ABC):
    def __init__(self):
        self.event_dispatcher = EventDispatcher(EventType)

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
