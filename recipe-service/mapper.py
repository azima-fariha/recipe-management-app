from models import Recipe
from schemas import RecipeDto, RecipeCreatedEvent

def to_dto(recipe: Recipe) -> RecipeDto:
    return RecipeDto(
        id=str(recipe.id),
        name=recipe.name,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions)

def to_model(recipe_dto: RecipeDto, user_id: str) -> Recipe:
    return Recipe(
        name=recipe_dto.name,
        ingredients=recipe_dto.ingredients,
        instructions=recipe_dto.instructions,
        user_id=user_id)

