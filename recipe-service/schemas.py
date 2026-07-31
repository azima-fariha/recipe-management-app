from pydantic import BaseModel
from typing import Optional

class RecipeDto(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    ingredients: list[str]
    instructions: str
    
class RecipeCreatedEvent(BaseModel):
    id: str
    name: str
    description: str
    ingredients: list[str]
    instructions: str
        