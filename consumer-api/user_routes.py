from fastapi import APIRouter, Request, Response
import httpx
from config import RECIPE_SERVICE_URL
from schemas import UserDto
import logging
import user_api
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/user/{user_id}")
async def get_user(user_id: int, request: Request) -> UserDto:
    logger.info(f"Received user request to fetch user id with %s", user_id)
    http_client = request.state.http_client
    user = await user_api.fetch_user(http_client, user_id)
    return UserDto(**user)

@router.post("/user")
async def create_user(userRequest: UserDto, request: Request)-> UserDto:
    logger.info(f"Received request to create a new user")
    http_client = request.state.http_client
    user = await user_api.create_user(http_client, userRequest.dict(exclude={"created_at"}))
    return UserDto(**user)
  

