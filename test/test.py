# import requi9red module
import sys

# append the path of the
# parent directory
sys.path.append(".")

# import method from sibling
# module
from UkatonMissionSDK import UDPUkatonMission, BLEUkatonMission

ukaton_mission = UDPUkatonMission()

print("udp")
