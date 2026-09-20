import logging

import user_routes
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)

app = FastAPI(title="user-service")

app.include_router(user_routes.router)
