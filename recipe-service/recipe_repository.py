from bson import ObjectId
from database import get_recipe_collection


async def get_recipe_by_id(recipe_id: str):
    collection = get_recipe_collection()
    return await collection.find_one({"_id": ObjectId(recipe_id)})

async def create_recipe(recipe_data: dict):
    collection = get_recipe_collection()
    return await collection.insert_one(recipe_data)
