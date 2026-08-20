from typing import Optional
from beanie import PydanticObjectId
from models import Recipe

async def get_recipe_by_id(recipe_id: str) -> Optional[Recipe]:
    return await Recipe.get(PydanticObjectId(recipe_id))

async def create_recipe(recipe: Recipe) -> Recipe:
    return await recipe.insert()

async def update_recipe(recipe: Recipe) -> Recipe:
    return await recipe.save()

async def delete_recipe(recipe: Recipe) -> None:
    await recipe.delete()