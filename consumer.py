import aio_pika
import pika
from aiokafka import AIOKafkaConsumer
from redis import asyncio as redis

from CONSTANTS import (
    EXCHANGE_NAME,
    KAFKA_SERVER,
    RABBITMQ_URL,
    TOPIC,
    REDIS_URL,
    CHANNEL,
)


async def pika_generator():
    connection = pika.BlockingConnection(pika.connection.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange="logs", queue=queue_name)
    print(" [*] Waiting for logs. To exit press CTRL+C")

    for method_frame, properties, body in channel.consume(queue_name):
        print(body)
        message = body.decode("utf-8")
        yield message + " - with pika!"
        channel.basic_ack(method_frame.delivery_tag)

        if message == "DONE":
            print("DONE")
            break

    channel.cancel()
    channel.close()
    connection.close()


async def aio_pika_generator():
    connection = await aio_pika.connect(RABBITMQ_URL)
    async with connection:

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        logs_exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT
        )
        queue = await channel.declare_queue(exclusive=True)

        await queue.bind(logs_exchange)
        print(" [*] Waiting for logs. To exit press CTRL+C")

        async for msg in queue:
            async with msg.process():
                # Display the message parts
                print(msg.body)
                message = msg.body.decode("utf-8")
                yield message + " - with aio_pika!"

                if message == "DONE":
                    print("DONE")
                    break


async def kafka_generator():
    consumer = AIOKafkaConsumer(TOPIC, bootstrap_servers=KAFKA_SERVER)
    await consumer.start()
    try:
        async for msg in consumer:
            print(
                msg.value,
            )
            message = msg.value.decode("utf-8")
            yield message + " - with aiokafka!"
            if message == "DONE":
                print("DONE")
                break
    finally:
        await consumer.stop()


async def redis_generator():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL)
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True)
            if msg is not None:
                print(f"(Reader) Message Received: {msg}")
                message = msg["data"]
                yield message + " - with redis"
                if message == "DONE":
                    print("DONE")
                    break
    finally:
        await r.close()
