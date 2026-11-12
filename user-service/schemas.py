import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserDto(BaseModel):
    id: Optional[int] = None
    full_name: str
    email: EmailStr
    dietary_restrictions: Optional[str] = None
    preferences: Optional[str] = None
    created_at: Optional[datetime.datetime] = None

class UserCreateDto(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    dietary_restrictions: Optional[str] = None
    preferences: Optional[str] = None

class UserUpdateDto(BaseModel):
    full_name: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    preferences: Optional[str] = None

class CredentialsDto(BaseModel):
    email: EmailStr
    password: str
