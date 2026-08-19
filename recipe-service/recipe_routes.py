import logging
from fastapi import APIRouter, Request
from fastapi.responses import Response
from schemas import RecipeDto, RecipeUpdateDto
import recipe_service
import mapper
import kafka_producer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["recipes"])

@router.get("/user/{user_id}/recipe/{recipe_id}")
async def get_recipe(user_id: str, recipe_id: str) -> RecipeDto:
    logger.info("Received request to fetch recipe with user_id: %s recipe_id: %s ", user_id, recipe_id)
    recipe = await recipe_service.get_recipe_by_id(user_id, recipe_id)
    return mapper.to_dto(recipe)

@router.post("/user/{user_id}/recipe")
async def create_recipe(user_id: str, recipeRequest: RecipeDto, request: Request) -> RecipeDto:
   logger.info("Received request to create recipe with user_id: %s", user_id)
   recipe = mapper.to_model(recipeRequest, user_id)
   recipe = await recipe_service.create_recipe(recipe)
   
   producer = request.state.kafka_producer
   await kafka_producer.publish_event(producer, recipe)
   
   return mapper.to_dto(recipe)

@router.put("/user/{user_id}/recipe/{recipe_id}")
async def update_recipe(user_id: str, recipe_id: str, recipeRequest: RecipeUpdateDto, request: Request) -> RecipeDto:
    logger.info("Received request to update recipe with user_id: %s recipe_id: %s", user_id, recipe_id)
    recipe = await recipe_service.get_recipe_by_id(user_id, recipe_id)
    updated_recipe = await recipe_service.update_recipe(recipe, recipeRequest)
    
    producer = request.state.kafka_producer
    await kafka_producer.publish_event(producer, updated_recipe)
       
    return mapper.to_dto(updated_recipe)

@router.delete("/user/{user_id}/recipe/{recipe_id}")
async def delete_recipe(user_id: str, recipe_id: str, request: Request) -> None:
    logger.info("Received request to delete recipe with user_id: %s recipe_id: %s", user_id, recipe_id)
    recipe = await recipe_service.get_recipe_by_id(user_id, recipe_id)
    await recipe_service.delete_recipe(recipe)

    producer = request.state.kafka_producer
    await kafka_producer.publish_deletion_event(producer, recipe_id)
    
    return Response(status_code=204)
