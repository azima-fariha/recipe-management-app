import logging
import os
from httpx import AsyncClient
from schemas import DiscoverRequest

AGENT_SERVICE_URL = os.environ.get("AGENT_SERVICE_URL", "http://localhost:8084")

async def discover_recipe(client: AsyncClient, user_id: str, discoverRequest: DiscoverRequest):
    logging.info("Calling agent-service with user_id %s, ingredients: %s", user_id, discoverRequest.query)
    response = await client.post(f"{AGENT_SERVICE_URL}/user/{user_id}/discover-recipes", json=discoverRequest.dict())
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()
