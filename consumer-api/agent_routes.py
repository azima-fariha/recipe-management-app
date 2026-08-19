from fastapi import APIRouter, HTTPException, Request
import logging
import agent_api
from schemas import DiscoverRequest, RecipeDto

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])


@router.post("/user/{user_id}/inspiration")
async def discover_recipe(user_id: str, ingredients: DiscoverRequest, request: Request) -> RecipeDto:
    logger.info(f"Received request to discover recipes for user_id: %s with ingredients: %s", user_id, ingredients.query)
    http_client = request.state.http_client
    recipe = await agent_api.discover_recipe(http_client, user_id, ingredients)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"No recipes found for user_id: {user_id}")
    return RecipeDto(**recipe)
