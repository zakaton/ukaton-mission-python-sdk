from UkatonMissionSDK.base import BaseUkatonMission, BaseUkatonMissions


class BLEUkatonMission(BaseUkatonMission):
    def connect(self, device_name: str):
        pass

    def disconnect(self):
        pass

    def _send_sensor_data_configuration(self, sensor_data_configuration: dict[str, dict[str, int]]):
        pass

    def _send_vibration(self, message: bytearray):
        pass


class BLEUkatonMissions(BaseUkatonMissions):
    pass
