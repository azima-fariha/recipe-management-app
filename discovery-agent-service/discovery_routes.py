import logging
from fastapi import APIRouter, Request
from prompts import discover_recipes_prompt
from schemas import DiscoverRequest, RecipeResult


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/user/{user_id}/discover-recipes")
async def discover_recipes(user_id: str, body: DiscoverRequest, request: Request) -> RecipeResult:
    logger.info("Received request to discover recipes for user_id: %s, query: %s", user_id, body.query)
    agent = request.state.recipe_agent
    messages = discover_recipes_prompt.format_messages(user_id=user_id, query=body.query)
    response = await agent.ainvoke({"messages": messages})
    result = response["structured_response"]
    logger.info("Found recipe for user_id: %s: %s", user_id, result.name)
    return result
