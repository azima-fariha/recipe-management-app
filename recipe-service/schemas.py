from pydantic import BaseModel
from typing import Optional

class RecipeDto(BaseModel):
    id: Optional[str] = None
    name: str
    ingredients: list[str]
    instructions: str
    
class RecipeUpdateDto(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[list[str]] = None
    instructions: Optional[str] = None    
    
class RecipeCreatedEvent(BaseModel):
    id: str
    name: str
    ingredients: list[str]
    instructions: str
    user_id: str

        