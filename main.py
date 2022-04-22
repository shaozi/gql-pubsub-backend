import graphene
from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from consumer import (
    pika_generator,
    aio_pika_generator,
    kafka_generator,
    redis_generator,
)


class Query(graphene.ObjectType):
    hello = graphene.String()

    async def resolve_hello(root, info):
        return "world"


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

app = Starlette()
app.mount("/", GraphQLApp(schema, on_get=make_graphiql_handler()))  # Graphiql IDE
