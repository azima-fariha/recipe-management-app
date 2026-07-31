import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserDto(BaseModel):
    id: Optional[int]
    full_name: Optional[str] = None
    email: EmailStr
    created_at: Optional[datetime.datetime] = None
    dietary_restrictions: Optional[str] = None
    
class RecipeDto(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    ingredients: list[str]
    instructions: str
        