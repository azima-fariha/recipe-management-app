import logging

import auth
import user_api
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from ownership import require_ownership
from schemas import TokenResponseDto, UserCreateDto, UserDto, UserUpdateDto

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])

# Note: none of these routes catch httpx.HTTPStatusError themselves — a
# shared handler registered on the app (see main.py) translates user-service's
# non-2xx responses into this gateway's own response for every route at once.

@router.get("/user/{user_id}", dependencies=[Depends(require_ownership)])
async def get_user(user_id: int, request: Request) -> UserDto:
    logger.info("Received user request to fetch user id with %s", user_id)
    http_client = request.state.http_client
    user = await user_api.fetch_user(http_client, user_id)
    return UserDto(**user)

@router.post("/user")
async def create_user(userRequest: UserCreateDto, request: Request) -> TokenResponseDto:
    logger.info("Received request to create a new user")
    http_client = request.state.http_client
    user = await user_api.create_user(http_client, userRequest.model_dump())

    # Signup logs the user in immediately: mint an Access Token alongside the created user.
    access_token = auth.create_access_token(str(user["id"]))
    return TokenResponseDto(access_token=access_token, user=UserDto(**user))

@router.put("/user/{user_id}", dependencies=[Depends(require_ownership)])
async def update_user(user_id: int, userRequest: UserUpdateDto, request: Request) -> UserUpdateDto:
    logger.info("Received request to update user with id %s", user_id)
    http_client = request.state.http_client
    user = await user_api.update_user(http_client, user_id, userRequest.dict(exclude_unset=True))
    return UserUpdateDto(**user)

@router.delete("/user/{user_id}", dependencies=[Depends(require_ownership)])
async def delete_user(user_id: str, request: Request):
    logger.info("Received request to delete user with id %s", user_id)
    http_client = request.state.http_client
    await user_api.delete_user(http_client, user_id)
    return Response(status_code=204)
