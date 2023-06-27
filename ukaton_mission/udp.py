from ukaton_mission.base import BaseUkatonMission, BaseUkatonMissions


class UDPUkatonMission(BaseUkatonMission):
    def connect(device_name: str):
        pass

    def disconnect(device_name: str):
        pass

    def set_sensor_data_configuration(sensor_data_configuration: dict[str, dict[str, int]]):
        pass

    def vibrate_waveform(waveform: list[int]):
        pass

    def vibrate_sequence(sequence: list[int]):
        pass


class UDPUkatonMissions(BaseUkatonMissions):
    pass
