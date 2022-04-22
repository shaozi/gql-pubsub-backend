#!/usr/bin/env python
import time

import pika

from CONSTANTS import EXCHANGE_NAME, RABBITMQ_URL, TOTAL, INTERVAL

connection = pika.BlockingConnection(pika.connection.URLParameters(RABBITMQ_URL))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout")

for i in range(TOTAL):
    message = f"{i} Hello World from RabbitMQ!"
    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="", body=message)
    print(" [x] Sent %r" % message)
    time.sleep(INTERVAL)

channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="", body="DONE")
connection.close()
