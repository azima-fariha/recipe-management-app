import logging

import security
import user_repository
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import User
from schemas import CredentialsDto, UserCreateDto, UserDto, UserUpdateDto
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])

@router.get("/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserDto:
    logger.info("Received request to fetch user with id: %s", user_id)
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        logger.warning("User with id %s not found", user_id)
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user

@router.post("/user")
async def create_user(userRequest: UserCreateDto, db: Session = Depends(get_db)) -> UserDto:
    logger.info("Received requests to create user")
    user = User(
        full_name = userRequest.full_name,
        email = userRequest.email,
        password_hash = security.hash_password(userRequest.password),
        dietary_restrictions = userRequest.dietary_restrictions,
        preferences = userRequest.preferences)
    try:
        return user_repository.create_user(db, user)
    except user_repository.DuplicateEmailError as exc:
        logger.warning("Signup rejected: %s", exc)
        raise HTTPException(status_code=409, detail="Email is already registered") from exc

@router.put("/user/{user_id}")
async def update_user(user_id: int, userRequest: UserUpdateDto, db: Session = Depends(get_db)) -> UserUpdateDto:
    logger.info("Received request to update user with id: %s", user_id)
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        logger.warning("User with id %s not found", user_id)
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    updated_user = user_repository.update_user(db, user, userRequest)
    return updated_user

@router.post("/internal/users/verify-credentials", tags=["internal"])
async def verify_credentials(credentials: CredentialsDto, db: Session = Depends(get_db)) -> UserDto:
    """Internal-only: called by consumer-api over the Docker network, never exposed publicly.

    Returns the matching user on a correct email+password pair. Returns the same
    401 for an unknown email and a wrong password, so the response never reveals
    which emails are registered.
    """
    logger.info("Received internal request to verify credentials")
    user = user_repository.get_user_by_email(db, credentials.email)
    if user is None or not security.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    logger.info("Received request to delete user with id: %s", user_id)
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        logger.warning("User with id %s not found", user_id)
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    user_repository.delete_user(db, user)
    return None

