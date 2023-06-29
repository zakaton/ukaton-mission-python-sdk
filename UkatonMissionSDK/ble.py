from UkatonMissionSDK.base import BaseUkatonMission, BaseUkatonMissions


class BLEUkatonMission(BaseUkatonMission):
    def connect(self, device_name: str):
        self.device_name: str = device_name
        pass

    def disconnect(self):
        pass

    def _send_sensor_data_configuration(self, serialized_sensor_data_configuration: bytearray):
        pass

    def _send_vibration(self, message: bytearray):
        pass


class BLEUkatonMissions(BaseUkatonMissions):
    pass
