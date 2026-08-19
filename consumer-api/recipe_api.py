import httpx
import logging
from httpx import AsyncClient
from config import RECIPE_SERVICE_URL

async def fetch_recipe(client: AsyncClient, user_id: str, recipe_id: str):
    logging.info("Calling recipe-service with user_id %s, recipe_id: %s", user_id, recipe_id)
    response = await client.get(f"{RECIPE_SERVICE_URL}/user/{user_id}/recipe/{recipe_id}")
    response.raise_for_status()
    return response.json()

async def create_recipe(client: AsyncClient, user_id: str, recipe_data: dict):
    logging.info("Calling recipe-service to create a new recipe with user_id: %s", user_id)
    response = await client.post(f"{RECIPE_SERVICE_URL}/user/{user_id}/recipe", json=recipe_data)
    response.raise_for_status()
    return response.json()

async def update_recipe(client: AsyncClient, user_id: str, recipe_id: str, recipe_data: dict):
    logging.info("Calling recipe-service to update recipe with user_id: %s, recipe_id: %s", user_id, recipe_id)
    response = await client.put(f"{RECIPE_SERVICE_URL}/user/{user_id}/recipe/{recipe_id}", json=recipe_data)
    response.raise_for_status()
    return response.json()

async def delete_recipe(client: AsyncClient, user_id: str, recipe_id: str):
    logging.info("Calling recipe-service to delete recipe with user_id: %s, recipe_id: %s", user_id, recipe_id)
    response = await client.delete(f"{RECIPE_SERVICE_URL}/user/{user_id}/recipe/{recipe_id}")
    response.raise_for_status()
