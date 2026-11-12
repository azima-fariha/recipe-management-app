import logging

import auth
import httpx
import user_api
from fastapi import APIRouter, HTTPException, Request
from schemas import LoginDto, TokenResponseDto, UserDto

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

@router.post("/auth/login")
async def login(loginRequest: LoginDto, request: Request) -> TokenResponseDto:
    logger.info("Received login request")
    http_client = request.state.http_client
    try:
        user = await user_api.verify_credentials(
            http_client, loginRequest.email, loginRequest.password
        )
    except httpx.HTTPStatusError as ex:
        raise HTTPException(status_code=ex.response.status_code, detail=ex.response.text) from ex

    access_token = auth.create_access_token(str(user["id"]))
    return TokenResponseDto(access_token=access_token, user=UserDto(**user))
