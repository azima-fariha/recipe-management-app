import json
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiokafka import AIOKafkaProducer
from contextlib import asynccontextmanager
import recipe_routes
from database import init_db
from exceptions import AppError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

# Runs once at startup and once at shutdown, wrapping the app's entire lifetime.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    producer = AIOKafkaProducer(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
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


@app.exception_handler(AppError)
async def app_error_handler(request: Request, ex: AppError):
    return JSONResponse(status_code=ex.status_code, content={"reason": ex.reason})
