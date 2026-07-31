import json
from fastapi import FastAPI
from aiokafka import AIOKafkaProducer
from contextlib import asynccontextmanager
import recipe_routes

# Runs once at startup and once at shutdown, wrapping the app's entire lifetime.
@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        # Auto-encode values/keys to bytes so routes can send plain dicts/strings.
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )
    await producer.start()

    # Whatever is yielded here is exposed as request.state.* in route handlers.
    yield {"kafka_producer": producer}

    # Runs on shutdown, after the yield, to release the connection cleanly.
    await producer.stop()

app = FastAPI(lifespan=lifespan)




app.include_router(recipe_routes.router)