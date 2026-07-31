from fastapi import FastAPI
import user_routes

app = FastAPI()

app.include_router(user_routes.router)
