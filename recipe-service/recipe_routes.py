import logging
from fastapi import APIRouter, HTTPException, Request
from schemas import RecipeDto, RecipeCreatedEvent
import recipe_repository
from recipe_repository import get_recipe_by_id
from aiokafka import AIOKafkaProducer

# Kafka topic name other services (e.g. the embedding service) subscribe to for new recipes.
RECIPE_CREATED_TOPIC = "recipe-created"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["recipes"])

@router.get("/recipe/{recipe_id}")
async def get_recipe(recipe_id: str) -> RecipeDto:
    logger.info("Received request to fetch recipe with id: %s", recipe_id)
    recipe = await get_recipe_by_id(recipe_id)
    if recipe is None:
        logger.warning("Recipe with id %s not found", recipe_id)
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeDto(**recipe, id=str(recipe["_id"]))
    
@router.post("/recipe")
async def create_recipe(recipeRequest: RecipeDto, request: Request) -> RecipeDto:
   logger.info("Received request to create recipe")
   recipe_dict = recipeRequest.dict(exclude={"id"})  # id is assigned by Mongo on insert, not by the client
   recipe = await recipe_repository.create_recipe(recipe_dict)
   recipe_id = str(recipe.inserted_id)
   
   logger.info("Sending Kafka event with id: %s", recipe_id)
   producer: AIOKafkaProducer = request.state.kafka_producer
   event = RecipeCreatedEvent(**recipe_dict, id=recipe_id)
   await producer.send_and_wait(RECIPE_CREATED_TOPIC, key=recipe_id, value=event.dict())

   return RecipeDto(**recipe_dict, id=recipe_id)
