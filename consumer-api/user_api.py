import httpx
import logging
from httpx import AsyncClient

async def fetch_user(client: AsyncClient, user_id: str):
    logging.info("Calling user service with id %s", user_id)
    response = await client.get(f"http://localhost:8081/user/{user_id}")
    return response.json()

async def create_user(client: AsyncClient, user_data: dict):
    logging.info("Calling user service to create a user.")
    response = await client.post("http://localhost:8081/user", json=user_data)
    return response.json()

