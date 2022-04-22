import asyncio

from aiokafka import AIOKafkaClient, AIOKafkaProducer

from CONSTANTS import INTERVAL, KAFKA_SERVER, TOPIC, TOTAL


async def send():
    client = AIOKafkaClient(bootstrap_servers=KAFKA_SERVER)
    client.add_topic(TOPIC)
    await client.close()

    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)
    await producer.start()
    try:
        for i in range(TOTAL):
            message = f"{i} Hello World from Kafka!"
            await producer.send_and_wait(TOPIC, bytes(message, "utf-8"))
            print(" [x] Sent %r" % message)
            await asyncio.sleep(INTERVAL)
        await producer.send_and_wait(TOPIC, b"DONE")
    finally:
        await producer.stop()


asyncio.run(send())
