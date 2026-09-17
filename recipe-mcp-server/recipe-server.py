import logging
import os

import requests
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Recipe Server")

RECIPE_EMBEDDING_SERVICE_URL = os.environ.get("RECIPE_EMBEDDING_SERVICE_URL", "http://localhost:8083")

@mcp.tool()
def get_recipe_by_ingredient(user_id: str, ingredients: str) -> list[dict]:
    """
    Get recipes by ingredient
    """
    logger.info("Tool get_recipe_by_ingredient called with user_id: %s, ingredients: %s", user_id, ingredients)
    response = requests.post(
        f"{RECIPE_EMBEDDING_SERVICE_URL}/user/{user_id}/recipe-by-ingredients",
        json={"ingredientRequest": ingredients}
    )
    logger.info("Tool get_recipe_by_ingredient got %d result(s) for user_id: %s", len(response.json()), user_id)
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8085)
