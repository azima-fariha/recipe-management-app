import logging
import recipe_repository
from schemas import RecipeUpdateDto
from models import Recipe
from exceptions import NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)

async def get_recipe_by_id(user_id: str, recipe_id: str) -> Recipe:
    recipe = await recipe_repository.get_recipe_by_id(recipe_id)
    
    if recipe is None:
        logger.warning("Recipe with id %s not found", recipe_id)
        raise NotFoundError(reason=f"Recipe with id {recipe_id} not found")
        
    if (recipe.user_id != user_id):
        logger.warning("User %s is not authorized to access recipe with id %s", user_id, recipe_id)
        raise ForbiddenError(reason=f"User {user_id} is not authorized to access recipe with id {recipe_id}")
    
    return recipe

async def create_recipe(recipe: Recipe) -> Recipe:
    logger.info("Creating recipe with name %s", recipe.name)
    created_recipe = await recipe_repository.create_recipe(recipe)
    logger.info("Recipe with id %s created successfully", created_recipe.id)
    
    return created_recipe

async def update_recipe(recipe: Recipe, updateRequest: RecipeUpdateDto) -> Recipe:
    logger.info("Updating recipe with id %s", recipe.id)
        
    if updateRequest.name is not None:
        recipe.name = updateRequest.name
    if updateRequest.ingredients is not None:
        recipe.ingredients = updateRequest.ingredients
    if updateRequest.instructions is not None:
        recipe.instructions = updateRequest.instructions
        
    updated_recipe = await recipe_repository.update_recipe(recipe)
    logger.info("Recipe with id %s updated successfully", recipe.id)
    
    return updated_recipe

async def delete_recipe(recipe: Recipe) -> None:
    logger.info("Deleting recipe with id %s", recipe.id)
    await recipe_repository.delete_recipe(recipe)
    logger.info("Recipe with id %s deleted successfully", recipe.id)
