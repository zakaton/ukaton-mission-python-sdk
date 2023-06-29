from UkatonMissionSDK.base import BaseUkatonMission, BaseUkatonMissions


class UDPUkatonMission(BaseUkatonMission):
    def connect(self, device_ip_address: str):
        self.device_ip_address: str = device_ip_address
        pass

    def disconnect(self):
        pass

    def _send_sensor_data_configuration(self, serialized_sensor_data_configuration: bytearray):
        pass

    def _send_vibration(self, message: bytearray):
        pass


class UDPUkatonMissions(BaseUkatonMissions):
    pass
