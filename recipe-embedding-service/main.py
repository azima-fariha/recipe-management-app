import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

import vector_routes
import vector_service
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI
from schemas import RecipeCreatedEvent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

RECIPE_KAFKA_TOPIC = "recipe-log"

@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = AIOKafkaConsumer(
                    RECIPE_KAFKA_TOPIC,
                    bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
                    group_id="recipe-embedding-service",
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v is not None else None,
                    key_deserializer=lambda k: k.decode("utf-8"),
                    auto_offset_reset="earliest")
    
    await consumer.start()
    
    task = asyncio.create_task(consume_recipe_events(consumer))

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await consumer.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(vector_routes.router)


async def consume_recipe_events(consumer: AIOKafkaConsumer):
    logger.info("Starting Kafka consumer.")
    async for msg in consumer:
        key = msg.key
        raw_value = msg.value #dict
        
        try:
            if key is None:
                logger.error("Skipping event because the key is null")
                continue

            if raw_value is None:
                logger.info("Received tombstone event for recipe id=%s", key)
                await asyncio.to_thread(vector_service.delete_recipe, key)
                continue
            
            logger.info("Received event with key=%s and value=%s", key, raw_value)
            recipe = RecipeCreatedEvent.model_validate(raw_value)
            await asyncio.to_thread(vector_service.vectorize_recipe, recipe)
        except Exception:
            logger.exception("Failed to process event with key=%s", key)
