from fastapi import APIRouter, Depends, HTTPException, Response
import logging
import user_repository
from database import get_db
from sqlalchemy.orm import Session
from schemas import UserDto
from models import User

logging.basicConfig(level=logging.INFO)
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
async def create_user(userRequest: UserDto, db: Session = Depends(get_db)) -> UserDto:
    logger.info("Received requests to create user")
    user = User(
        full_name = userRequest.full_name,
        email = userRequest.email,
        dietary_restrictions = userRequest.dietary_restrictions)
    return user_repository.create_user(db, user)
