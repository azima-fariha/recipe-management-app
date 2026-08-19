import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserDto(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = None
    email: EmailStr
    created_at: Optional[datetime.datetime] = None
    dietary_restrictions: Optional[str] = None
    preferences: Optional[str] = None
    
class UserUpdateDto(BaseModel):
    full_name: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    preferences: Optional[str] = None    
    
class RecipeDto(BaseModel):
    id: Optional[str] = None
    name: str
    ingredients: list[str]
    instructions: str
    
class RecipeUpdateDto(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[list[str]] = None
    instructions: Optional[str] = None    
    
class DiscoverRequest(BaseModel):
    query: str
