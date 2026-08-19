import logging
from fastapi import APIRouter
import vector_service
from schemas import IngredientRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["recipes"])

@router.post("/user/{user_id}/recipe-by-ingredients")
async def retrieve_recipe_by_ingredient(user_id: str, body: IngredientRequest):
   logger.info("Received request to find similar recipes for user_id: %s with ingredients: %s", user_id, body.ingredientRequest)
   results = vector_service.retrieve_similar_texts_by_user(user_id, body.ingredientRequest)
   if not results:
      logger.info("No recipe found for user_id: %s with the provided ingredient list", user_id)
   return results
