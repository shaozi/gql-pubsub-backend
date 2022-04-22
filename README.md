# Pub/Sub with GraphQL and RabbitMQ, Kafka and Redis

In this example, we explored GraphQL Subscription back end implementations 
with two three message brokers: RabbitMQ, Kafka and Redis.

We will use python to implement this example. 
The libraries we will use are:

- starlette-graphene3
- uvicorn[standard]
- pika
- aio-pika
- aiokafka
- redis


## GraphQL Subscription

GraphQL defines a `subscription` method to allow the front end to receive real time updates through a websocket connection.

A typical use case of this feature is to monitor and update a status change in real time. Another use case is to display a stream of logs in real time. 

## Message Broker and Pub/Sub

GraphQL's subscription feature requires the back end to be able to send data from one source to multiple destinations. The data is called `message`, and the
one to many distribution of the message is called `fan-out`. 

A message brokders decouples the message sending and receiving functions. A message is published to the broker by a `producer`,
and the broker delivers the message to the `consumer` who subscribes to receive the message. This is called **Pub/Sub**. The producer only needs to know how to publish to the broker, and the consumers only need to know how to subscribe from the broker.

Because of the seperation of producer and consumer, Pub/Sub model simplifies both the producer and the consumer. 
It makes the message distribution more efficient, reliable, and scalable.

## Example 

### Start rabbitmq and kafka containers in docker

```sh
docker compose -f docker-compose.yaml up &
```

### Install the libraries

We use `pdm` to manage dependencies. You can use vanilla `pip` or other tools such
as `poetry` and `pipenv`.

```sh
pdm add starlette-graphene3 'uvicorn[standard]' pika aio-pika aiokafka redis
```

### GraphQL server

We setup a simple starlette uvicorn web server
with graphene. Libraries: `starlette-graphene3 'uvicorn[standard]'`


#### Create a web server

Create a simple server `main.py` and add a `Subscription` class:

```python

class Subscription(graphene.ObjectType):
    message = graphene.String(consumer=graphene.String(default_value="redis"))

    async def subscribe_message(root, info, consumer):
        if consumer == "pika":
            f = pika_generator
        elif consumer == "aio_pika":
            f = aio_pika_generator
        elif consumer == "kafka":
            f = kafka_generator
        else:
            f = redis_generator
        async for message in f():
            yield message

schema = graphene.Schema(query=Query, subscription=Subscription)

```

This class defines a GraphQL subscription. It is a Pub/Sub consumer. It takes a `consumer` argument to decide which library to use to consume the message. The `Async for` loop will wait the message from the publisher
and send it to the front end until there are no more messages.

The details of the consumer are in file `consumer.py`.

#### Start the server

```sh
pdm run uvicorn main:app
```


## RabbitMQ







