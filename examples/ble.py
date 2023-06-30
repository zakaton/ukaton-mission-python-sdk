import sys
sys.path.append(".")

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from UkatonMissionSDK import BLEUkatonMission, ConnectionEventType
ukaton_mission = BLEUkatonMission()

import asyncio


def on_connection():
    logger.debug("connected callback triggered :)")


def on_disconnection():
    logger.debug("disconnected callback triggered :O")


async def main():
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.CONNECTED, on_connection)
    ukaton_mission.connection_event_dispatcher.add_event_listener(
        ConnectionEventType.DISCONNECTED, on_disconnection)

    await ukaton_mission.connect("missionDevice")
    # FILL - trigger callbacks...
    await asyncio.sleep(3)
    await ukaton_mission.disconnect()
    await asyncio.sleep(3)
    logger.debug("end of main ;)")

asyncio.run(main())
