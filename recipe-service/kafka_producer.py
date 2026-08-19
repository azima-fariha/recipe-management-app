import logging
from aiokafka import AIOKafkaProducer
from models import Recipe
from schemas import RecipeCreatedEvent

logger = logging.getLogger(__name__)

KAFKA_RECIPE_TOPIC = "recipe-created"

async def publish_event(kafka_producer: AIOKafkaProducer, recipe: Recipe):
    logger.info("Sending Kafka event with id: %s", recipe.id)
    event = RecipeCreatedEvent(
        id=str(recipe.id),
        name=recipe.name,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        user_id=recipe.user_id)
    await kafka_producer.send_and_wait(KAFKA_RECIPE_TOPIC, key=str(recipe.id), value=event.model_dump())

async def publish_deletion_event(kafka_producer: AIOKafkaProducer, recipe_id: str):
    logger.info("Sending Kafka tombstone event with id: %s", recipe_id)
    await kafka_producer.send_and_wait(KAFKA_RECIPE_TOPIC, key=recipe_id, value=None)
