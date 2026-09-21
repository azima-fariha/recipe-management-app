import logging
import os

from exceptions import NotFoundError
from httpx import AsyncClient

logger = logging.getLogger(__name__)

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8081")
    
async def fetch_user(client: AsyncClient, user_id: str):
    logger.info("Calling user service with id %s", user_id)
    response = await client.get(f"{USER_SERVICE_URL}/user/{user_id}")
    if response.status_code == 404:
        raise NotFoundError(f"User with id {user_id} not found.")
    
    response.raise_for_status()
    return response.json()