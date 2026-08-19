from fastapi import APIRouter, Request
from schemas import UserDto, UserUpdateDto
import logging
import user_api

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])

@router.get("/user/{user_id}")
async def get_user(user_id: int, request: Request) -> UserDto:
    logger.info(f"Received user request to fetch user id with %s", user_id)
    http_client = request.state.http_client
    user = await user_api.fetch_user(http_client, user_id)
    return UserDto(**user)

@router.post("/user")
async def create_user(userRequest: UserDto, request: Request) -> UserDto:
    logger.info(f"Received request to create a new user")
    http_client = request.state.http_client
    user = await user_api.create_user(http_client, userRequest.dict(exclude={"created_at"}))
    return UserDto(**user)

@router.put("/user/{user_id}")
async def update_user(user_id: int, userRequest: UserUpdateDto, request: Request) -> UserUpdateDto:
    logger.info(f"Received request to update user with id %s", user_id)
    http_client = request.state.http_client
    user = await user_api.update_user(http_client, user_id, userRequest.dict(exclude_unset=True))
    return UserUpdateDto(**user)