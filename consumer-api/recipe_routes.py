import logging

import recipe_api
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from ownership import require_ownership
from schemas import RecipeDto, RecipeUpdateDto

logger = logging.getLogger(__name__)

router = APIRouter(tags=["recipes"])

# Note: none of these routes catch httpx.HTTPStatusError themselves — a
# shared handler registered on the app (see main.py) translates recipe-service's
# non-2xx responses into this gateway's own response for every route at once.

@router.get("/user/{user_id}/recipe", dependencies=[Depends(require_ownership)])
async def list_recipes(user_id: str, request: Request) -> list[RecipeDto]:
    logger.info("Received user request to list recipes for user_id: %s", user_id)
    http_client = request.state.http_client
    recipes = await recipe_api.list_recipes(http_client, user_id)
    return [RecipeDto(**recipe) for recipe in recipes]

@router.get("/user/{user_id}/recipe/{recipe_id}", dependencies=[Depends(require_ownership)])
async def fetch_recipe(user_id: str, recipe_id:str, request: Request) -> RecipeDto:
    logger.info("Received user request to fetch recipe with user_id: %s, recipe_id: %s", user_id, recipe_id)
    http_client = request.state.http_client
    recipe = await recipe_api.fetch_recipe(http_client, user_id, recipe_id)
    return RecipeDto(**recipe)

@router.post("/user/{user_id}/recipe", dependencies=[Depends(require_ownership)])
async def create_recipe(user_id: str, recipeRequest: RecipeDto, request: Request)-> RecipeDto:
    logger.info("Received request to create a new recipe with user_id: %s", user_id)
    http_client = request.state.http_client
    recipe = await recipe_api.create_recipe(http_client, user_id, recipeRequest.dict())
    return RecipeDto(**recipe)

@router.put("/user/{user_id}/recipe/{recipe_id}", dependencies=[Depends(require_ownership)])
async def update_recipe(user_id: str, recipe_id:str, recipeRequest: RecipeUpdateDto, request: Request)-> RecipeDto:
    logger.info("Received request to update recipe with user_id: %s recipe_id: %s", user_id, recipe_id)
    http_client = request.state.http_client
    recipe = await recipe_api.update_recipe(http_client, user_id, recipe_id, recipeRequest.dict())
    return RecipeDto(**recipe)

@router.delete("/user/{user_id}/recipe/{recipe_id}", dependencies=[Depends(require_ownership)])
async def delete_recipe(user_id: str, recipe_id:str, request: Request):
    logger.info("Received request to delete recipe with user_id: %s recipe_id: %s", user_id, recipe_id)
    http_client = request.state.http_client
    await recipe_api.delete_recipe(http_client, user_id, recipe_id)
    return Response(status_code=204)
