from UkatonMissionSDK.base import BaseUkatonMission, BaseUkatonMissions
from UkatonMissionSDK.enumerations import *

import socket
import threading
import asyncio
import time

import nest_asyncio
nest_asyncio.apply()

from typing import Optional

import logging
logging.basicConfig()
logger = logging.getLogger("UDPUkatonMission")
logger.setLevel(logging.DEBUG)


class UDPUkatonMission(BaseUkatonMission):
    LOCAL_IP: str = "0.0.0.0"
    LOCAL_PORT: int = 5005

    REMOTE_PORT: int = 9999

    def __init__(self):
        super().__init__()
        self.device_ip_address: Optional[str] = None
        self._did_receive_device_type: bool = False
        self._receive_device_type_future: Optional[asyncio.Future] = None
        self.socket: Optional[socket.socket] = None
        self.receive_thread: Optional[threading.Thread] = None
        self.ping_loop = asyncio.get_event_loop()

    async def connect(self, device_ip_address: str):
        self.device_ip_address = device_ip_address

        logger.debug("creating socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.__class__.LOCAL_IP, self.__class__.LOCAL_PORT))
        logger.debug("created socket")

        logger.debug("setting up receive thread...")
        self.receive_thread = threading.Thread(target=self.check_udp_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        logger.debug("set up receive thread")

        self._receive_device_type_future = asyncio.Future()
        # self._receive_device_type_future.set_result(None)
        self.ping_loop.run_until_complete(self.ping())
        return await self._receive_device_type_future

    async def disconnect(self):
        self.ping_loop.stop()
        self._did_receive_device_type = False

    def check_udp_messages(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            logger.debug(
                f'Received message from {addr[0]}:{addr[1]}: {data}')

    def ping(self):
        while True:
            message_byte = UDPMessageType.PING if self._did_receive_device_type else UDPMessageType.GET_TYPE
            self.send_message(bytearray([message_byte]))
            time.sleep(1)

    def send_message(self, message: bytearray):
        logger.debug(f"sending message: {message}")
        try:
            self.socket.sendto(
                message, (self.device_ip_address, self.__class__.REMOTE_PORT))
        except socket.error as e:
            # logger.debug(f"socket error: {e}")
            pass

    async def _send_sensor_data_configuration(self, serialized_sensor_data_configuration: bytearray):
        pass

    async def _send_vibration(self, message: bytearray):
        pass


class UDPUkatonMissions(BaseUkatonMissions):
    pass
