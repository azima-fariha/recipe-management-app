from pydantic import BaseModel, Field

class DiscoverRequest(BaseModel):
    query: str


class RecipeResult(BaseModel):
    name: str
    ingredients: list[str]
    instructions: str

