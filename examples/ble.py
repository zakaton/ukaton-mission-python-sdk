import sys
sys.path.append(".")

import asyncio

from UkatonMissionSDK import BLEUkatonMission

ukaton_mission = BLEUkatonMission()


async def main():
    await ukaton_mission.connect("missionDevice")
    await asyncio.sleep(10.0)

asyncio.run(main())
