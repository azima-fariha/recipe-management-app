import httpx
import logging
from httpx import AsyncClient

async def fetch_recipe(client: AsyncClient, recipe_id: str):
    logging.info("Calling recipe service with id %s", recipe_id)
    response = await client.get(f"http://localhost:8082/recipe/{recipe_id}")
    return response.json()

async def create_recipe(client: AsyncClient, recipe_data: dict):
    logging.info("Calling recipe service to create a new recipe")
    response = await client.post(f"http://localhost:8082/recipe", json=recipe_data)
    return response.json()
    