import os

from beanie import init_beanie
from models import Recipe
from pymongo import AsyncMongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

client = AsyncMongoClient(MONGO_URL)
database = client["recipe_db"]

async def init_db():
    await init_beanie(database=database, document_models=[Recipe])
