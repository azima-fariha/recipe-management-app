from typing import Optional
from pydantic import BaseModel, Field

class IngredientRequest(BaseModel):
    ingredientRequest: str


class RecipeCreatedEvent(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None
    ingredients: list[str] = Field(default_factory=list)
    instructions: Optional[str] = None

    def to_embedding_text(self) -> str:
        """Text fed to the embedding model - combines whatever fields are present."""
        parts = []
        if self.name:
            parts.append(f"Name: {self.name}")
        if self.ingredients:
            parts.append(f"Ingredients: {', '.join(self.ingredients)}")
        if self.instructions:
            parts.append(f"Instructions: {self.instructions}")
        return "\n".join(parts)