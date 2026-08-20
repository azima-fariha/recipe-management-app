from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
import recipe_routes
import user_routes
import agent_routes
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.AsyncClient(timeout=10.0)
    yield {"http_client": client}
    await client.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(recipe_routes.router)
app.include_router(user_routes.router)
app.include_router(agent_routes.router)