import redis
import time
import random

import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

r = redis.Redis(host="dmz_redis", port=6379, decode_responses=True)

# this is just for demonstration, not to be used in the demo

while True:
    # 1. Read what the OT side published
    data = r.get("ot_sensor_data")
    print(f"Dashboard - OT Sensor: {data}")

    # 2. Update a configuration value in the DMZ
    new_setpoint = int(random.random())
    r.set("it_config_setpoint", new_setpoint, ex=60)
    print(f"Dashboard - Sent new SetPoint: {new_setpoint}")

    time.sleep(1)
