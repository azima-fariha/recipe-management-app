from fastapi import APIRouter, Request, Response
import httpx
from config import RECIPE_SERVICE_URL
import recipe_api
import logging
from schemas import RecipeDto


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/recipe/{recipe_id}")
async def fetch_recipe(recipe_id:str, request: Request) -> RecipeDto:
    logger.info(f"Received user request to fetch recipe id with %s", recipe_id)
    http_client = request.state.http_client
    recipe = await recipe_api.fetch_recipe(http_client, recipe_id)
    return RecipeDto(**recipe)

@router.post("/recipe")
async def create_recipe(recipeRequest: RecipeDto, request: Request)-> RecipeDto:
    logger.info(f"Received request to create a new recipe")
    http_client = request.state.http_client
    recipe = await recipe_api.create_recipe(http_client, recipeRequest.dict())
    return RecipeDto(**recipe)
    

    