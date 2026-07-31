from motor.motor_asyncio import AsyncIOMotorClient

# Connection string for the local Mongo instance (see docker run command
# that published the container's port to localhost:27017)
MONGO_URL = "mongodb://localhost:27017"

# Client manages a pooled connection to the Mongo server for the app's
# lifetime. Unlike SQLAlchemy's engine, there's no separate session object
# to open/close per request - the client handles connections internally.
client = AsyncIOMotorClient(MONGO_URL)

# Grabs a reference to the "recipe_db" database. Mongo creates it lazily
# on first write, so there's no equivalent of Base.metadata.create_all().
database = client["recipe_db"]

# Reference to the "recipes" collection (Mongo's equivalent of a table).
# Created lazily too - repository functions call find_one()/insert_one()
# directly on this object.
recipes_collection = database["recipes"]

# FastAPI dependency (used via Depends() in routes) that hands the
# collection to route handlers. No open/close lifecycle needed here -
# unlike get_db()'s generator + yield/finally in user-service, Motor's
# collection object is safe to reuse across requests since the client
# already manages the connection pool.
def get_recipe_collection():
    return recipes_collection

