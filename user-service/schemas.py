import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserDto(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = None
    email: EmailStr
    created_at: Optional[datetime.datetime] = None
    dietary_restrictions: Optional[str] = None

class UserUpdateDto(BaseModel):
    full_name: Optional[str] = None
    dietary_restrictions: Optional[str] = None
