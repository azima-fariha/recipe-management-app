import logging

import auth
import user_api
from fastapi import APIRouter, Request
from schemas import LoginDto, TokenResponseDto, UserDto

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

@router.post("/auth/login")
async def login(loginRequest: LoginDto, request: Request) -> TokenResponseDto:
    logger.info("Received login request")
    http_client = request.state.http_client
    # Any non-2xx from user-service (e.g. bad credentials) propagates as
    # httpx.HTTPStatusError and is translated by the shared handler in main.py.
    user = await user_api.verify_credentials(
        http_client, loginRequest.email, loginRequest.password
    )

    access_token = auth.create_access_token(str(user["id"]))
    return TokenResponseDto(access_token=access_token, user=UserDto(**user))
