from fastapi import APIRouter, HTTPException, Request
import httpx
import recipe_api
import logging
from schemas import RecipeDto, RecipeUpdateDto
from fastapi.responses import Response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["recipes"])

@router.get("/user/{user_id}/recipe/{recipe_id}")
async def fetch_recipe(user_id: str, recipe_id:str, request: Request) -> RecipeDto:
    logger.info(f"Received user request to fetch recipe with user_id: %s, recipe_id: %s", user_id, recipe_id)
    http_client = request.state.http_client
    try:
        recipe = await recipe_api.fetch_recipe(http_client, user_id, recipe_id)
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex
    
    return RecipeDto(**recipe)

@router.post("/user/{user_id}/recipe")
async def create_recipe(user_id: str, recipeRequest: RecipeDto, request: Request)-> RecipeDto:
    logger.info(f"Received request to create a new recipe with user_id: %s", user_id)
    http_client = request.state.http_client
    try:
        recipe = await recipe_api.create_recipe(http_client, user_id, recipeRequest.dict())
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex

    return RecipeDto(**recipe)
    
@router.put("/user/{user_id}/recipe/{recipe_id}")
async def update_recipe(user_id: str, recipe_id:str, recipeRequest: RecipeUpdateDto, request: Request)-> RecipeDto:
    logger.info("Received request to update recipe with user_id: %s recipe_id: %s", user_id, recipe_id)
    http_client = request.state.http_client
    try:
        recipe = await recipe_api.update_recipe(http_client, user_id, recipe_id, recipeRequest.dict())
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex
    
    return RecipeDto(**recipe)

@router.delete("/user/{user_id}/recipe/{recipe_id}")
async def delete_recipe(user_id: str, recipe_id:str, request: Request):
    logger.info("Received request to delete recipe with user_id: %s recipe_id: %s", user_id, recipe_id)
    http_client = request.state.http_client
    try:
        await recipe_api.delete_recipe(http_client, user_id, recipe_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    
    return Response(status_code=204)
