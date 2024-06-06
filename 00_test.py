from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

import time

ChannelFactoryInitialize(0)

sport_client = SportClient()
sport_client.SetTimeout(10.0)
sport_client.Init()

print("Environment good to go!")

sport_client.StandDown()
time.sleep(1)
sport_client.StandUp()
time.sleep(1)
sport_client.StandDown()
time.sleep(1)
sport_client.StandUp()
time.sleep(1)
