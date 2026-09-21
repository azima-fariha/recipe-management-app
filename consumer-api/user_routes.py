import logging

import httpx
import user_api
from fastapi import APIRouter, HTTPException, Request
from schemas import UserDto, UserUpdateDto

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])

@router.get("/user/{user_id}")
async def get_user(user_id: int, request: Request) -> UserDto:
    logger.info("Received user request to fetch user id with %s", user_id)
    http_client = request.state.http_client
    try:
        user = await user_api.fetch_user(http_client, user_id)
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex
    
    return UserDto(**user)

@router.post("/user")
async def create_user(userRequest: UserDto, request: Request) -> UserDto:
    logger.info("Received request to create a new user")
    http_client = request.state.http_client
    try:
        user = await user_api.create_user(http_client, userRequest.dict(exclude={"created_at"}))
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex
        
    return UserDto(**user)

@router.put("/user/{user_id}")
async def update_user(user_id: int, userRequest: UserUpdateDto, request: Request) -> UserUpdateDto:
    logger.info("Received request to update user with id %s", user_id)
    http_client = request.state.http_client
    try:
        user = await user_api.update_user(http_client, user_id, userRequest.dict(exclude_unset=True))
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex
        
    return UserUpdateDto(**user)
