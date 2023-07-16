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
logger.setLevel(logging.ERROR)


class UDPUkatonMission(BaseUkatonMission):
    LOCAL_IP: str = "0.0.0.0"

    REMOTE_PORT: int = 9999

    def __init__(self):
        super().__init__()
        self.LOCAL_PORT: int = 5005
        self.device_ip_address: Optional[str] = None
        self._did_receive_device_type: bool = False
        self._receive_device_type_future: Optional[asyncio.Future] = None
        self.socket: Optional[socket.socket] = None
        self.check_udp_messages_thread: Optional[threading.Thread] = None
        self.check_udp_messages_thread_event: Optional[threading.Event] = None
        self.ping_thread: Optional[threading.Thread] = None
        self.ping_thread_event: Optional[threading.Event] = None
        self.check_connection_thread: Optional[threading.Thread] = None
        self.check_connection_thread_event: Optional[threading.Event] = None

    async def connect(self, device_ip_address: str):
        self.is_connecting = True

        self.device_ip_address = device_ip_address

        logger.debug("creating socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(
            (self.__class__.LOCAL_IP, self.LOCAL_PORT))
        logger.debug("created socket")

        logger.debug("setting up receive thread...")
        self.check_udp_messages_thread_event = threading.Event()
        self.check_udp_messages_thread = threading.Thread(
            target=self.check_udp_messages)
        self.check_udp_messages_thread.daemon = True
        self.check_udp_messages_thread.start()
        logger.debug("set up receive thread")

        self._receive_device_type_future = asyncio.Future()

        logger.debug("setting up ping...")
        self.ping_thread_event = threading.Event()
        self.ping_thread = threading.Thread(target=self.ping)
        self.ping_thread.daemon = True
        self.ping_thread.start()
        logger.debug("set up ping thread")

        def run_check_connection():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.create_task(self.check_connection())
            loop.run_forever()

        logger.debug("setting up check sensor data thread...")
        self.check_connection_thread_event = threading.Event()
        self.check_connection_thread = threading.Thread(
            target=run_check_connection)
        self.check_connection_thread.daemon = True
        self.check_connection_thread.start()
        logger.debug("set up check sensor data thread")

        return await self._receive_device_type_future

    async def disconnect(self):
        logger.debug("attempting to disconnect from device...")
        self.check_udp_messages_thread_event.set()
        self.ping_thread_event.set()
        self.check_connection_thread_event.set()
        self._did_receive_device_type = False
        _socket = self.socket
        self.socket = None
        _socket.close()
        self._disconnection_handler()

    def check_udp_messages(self):
        while self.socket is not None and not self.check_udp_messages_thread_event.is_set():
            data, addr = self.socket.recvfrom(1024)
            logger.debug(
                f'Received message from {addr[0]}:{addr[1]}: {data}')
            self.parse_udp_message(data)

    def parse_udp_message(self, data: bytes):
        byte_offset = 0
        data_len = len(data)
        while byte_offset < data_len:
            message_type = UDPMessageType(data[byte_offset])
            byte_offset += 1
            logger.debug(f"message_type: {message_type}")

            match message_type:
                case UDPMessageType.BATTERY_LEVEL:
                    byte_offset = self.parse_battery_level_data(
                        data, byte_offset)
                    break
                case UDPMessageType.GET_TYPE:
                    byte_offset = self.parse_device_type_data(
                        data, byte_offset)
                    if not self._did_receive_device_type:
                        self._did_receive_device_type = True
                        self.is_connected = True
                        self._connection_handler()
                        self._receive_device_type_future.get_loop().call_soon_threadsafe(
                            self._receive_device_type_future.set_result, None)
                        self._receive_device_type_future = None
                    break
                case UDPMessageType.SENSOR_DATA:
                    sensor_data = data[byte_offset:]
                    logger.debug(
                        f"sensor_data[{len(sensor_data)}]: {sensor_data}")
                    byte_offset = self.parse_sensor_data(sensor_data)
                    break
                case UDPMessageType.SET_SENSOR_DATA_CONFIGURATIONS:
                    byte_offset = data_len
                    break
                case _:
                    logger.debug(f"uncaught message_type: {message_type}")
                    break

    def ping(self):
        while not self.ping_thread_event.is_set():
            message_byte = UDPMessageType.PING if self._did_receive_device_type else UDPMessageType.GET_TYPE
            self.send_message(bytearray([message_byte]))
            time.sleep(1)

    async def check_connection(self):
        while not self.check_connection_thread_event.is_set():
            if self._sensor_data_configurations is not None:
                should_resend_sensor_data_configurations = time.time(
                ) - self._last_time_received_sensor_data > 2
                logger.debug(
                    f"should_resend_sensor_data_configurations? {should_resend_sensor_data_configurations}")
                if should_resend_sensor_data_configurations:
                    await self.set_sensor_data_configurations(
                        self._sensor_data_configurations)
            time.sleep(3)

    def send_message(self, message: bytearray):
        logger.debug(f"sending message: {message}")
        try:
            self.socket.sendto(
                message, (self.device_ip_address, self.__class__.REMOTE_PORT))
        except socket.error as e:
            # logger.debug(f"socket error: {e}")
            pass

    async def _send_sensor_data_configurations(self, serialized_sensor_data_configuration: bytearray):
        self.send_message(bytearray([UDPMessageType.SET_SENSOR_DATA_CONFIGURATIONS, len(
            serialized_sensor_data_configuration), *serialized_sensor_data_configuration]))

    async def _send_vibration(self, message: bytearray):
        self.send_message(
            bytearray([UDPMessageType.VIBRATION, len(message), *message]))


class UDPUkatonMissions(BaseUkatonMissions):
    UkatonMission = UDPUkatonMission
