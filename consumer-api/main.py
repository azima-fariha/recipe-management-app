from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
import recipe_routes
import user_routes

# Runs once at startup and once at shutdown, wrapping the app's entire lifetime.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # One shared, connection-pooled client for all proxied requests, instead
    # of opening a new connection per request.
    client = httpx.AsyncClient(timeout=10.0)

    # Whatever is yielded here is exposed as request.state.* in route handlers.
    yield {"http_client": client}

    # Runs on shutdown, after the yield, to release the connection pool cleanly.
    await client.aclose()

# lifespan must be passed here for the block above to actually run -
# defining it alone does nothing.
app = FastAPI(lifespan=lifespan)
app.include_router(recipe_routes.router)
app.include_router(user_routes.router)