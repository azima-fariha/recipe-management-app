import logging
import os
from fastmcp import FastMCP
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("User Server")

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8081")

@mcp.tool()
def get_user_by_id(user_id: str) -> dict:
    """
    Get user by id
    """
    logger.info("Tool get_user_by_id called with user_id: %s", user_id)
    response = requests.get(f"{USER_SERVICE_URL}/user/{user_id}")
    logger.info("Tool get_user_by_id got response status %s for user_id: %s", response.status_code, user_id)
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8086)