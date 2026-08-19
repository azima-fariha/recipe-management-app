import os
from pymongo import AsyncMongoClient
from beanie import init_beanie
from models import Recipe

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

# Client manages a pooled connection to the Mongo server for the app's
# lifetime. Unlike SQLAlchemy's engine, there's no separate session object
# to open/close per request - the client handles connections internally.
# Uses PyMongo's native async client rather than Motor - Motor is being
# phased out in favor of this, and Beanie 2.x targets it directly (Motor's
# client trips up Beanie's driver-metadata registration on startup).
client = AsyncMongoClient(MONGO_URL)

# Grabs a reference to the "recipe_db" database. Mongo creates it lazily
# on first write, so there's no equivalent of Base.metadata.create_all().
database = client["recipe_db"]

# Registers Beanie's Document models against this database, so Recipe.get(),
# Recipe.insert(), etc. know which client/collection to use under the hood.
# Beanie is the ODM layer here - it's what SQLAlchemy's User model is to
# MySQL in user-service, giving routes/repositories real objects instead of
# raw dicts. Must be awaited once at startup (see main.py's lifespan) before
# any Recipe query/insert is made.
async def init_db():
    await init_beanie(database=database, document_models=[Recipe])
