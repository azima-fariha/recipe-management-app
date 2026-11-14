import logging
from contextlib import asynccontextmanager

import agent_routes
import auth_routes
import httpx
import recipe_routes
import user_routes
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.AsyncClient(timeout=10.0)
    yield {"http_client": client}
    await client.aclose()

app = FastAPI(lifespan=lifespan, title="consumer-api")
app.include_router(recipe_routes.router)
app.include_router(user_routes.router)
app.include_router(agent_routes.router)
app.include_router(auth_routes.router)


@app.exception_handler(httpx.HTTPStatusError)
async def httpx_status_error_handler(request: Request, exc: httpx.HTTPStatusError) -> JSONResponse:
    """Translates a downstream service's non-2xx response into this
    gateway's own response, one level up from every route.

    Every route handler used to repeat
    `except httpx.HTTPStatusError as ex: raise HTTPException(status_code=ex.response.status_code,
    detail=ex.response.text) from ex` itself; this handler replaces all of
    those with the single behavior they shared — forward the downstream
    status code and body text as this gateway's own response, in the same
    `{"detail": ...}` shape FastAPI's own HTTPException renders.
    """
    return JSONResponse(status_code=exc.response.status_code, content={"detail": exc.response.text})
