import time
import redis
from CONSTANTS import REDIS_URL, CHANNEL, INTERVAL, TOTAL

r = redis.from_url(REDIS_URL)

for i in range(TOTAL):
    message = f"{i} Hello World from Redis!"
    r.publish(CHANNEL, message)
    print(" [x] Sent %r" % message)
    time.sleep(INTERVAL)

r.publish(CHANNEL, "DONE")
r.close()
