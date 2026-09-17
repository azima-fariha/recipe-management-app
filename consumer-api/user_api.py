import logging

from config import USER_SERVICE_URL
from httpx import AsyncClient
from schemas import UserUpdateDto

logger = logging.getLogger(__name__)

async def fetch_user(client: AsyncClient, user_id: str):
    logger.info("Calling user service with id %s", user_id)
    response = await client.get(f"{USER_SERVICE_URL}/user/{user_id}")
    return response.json()

async def create_user(client: AsyncClient, user_data: dict):
    logger.info("Calling user service to create a user.")
    response = await client.post(f"{USER_SERVICE_URL}/user", json=user_data)
    return response.json()

async def update_user(client: AsyncClient, user_id: str, user_data: UserUpdateDto):
    logger.info("Calling user service to update user with id %s", user_id)
    response = await client.put(f"{USER_SERVICE_URL}/user/{user_id}", json=user_data)
    return response.json()
