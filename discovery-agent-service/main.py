import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from fastapi import FastAPI
import discovery_routes
from prompts import DISCOVER_RECIPES_SYSTEM_PROMPT
from schemas import RecipeResult
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    recipe_mcp_url = os.environ.get("RECIPE_MCP_URL", "http://localhost:8085/mcp")
    user_mcp_url = os.environ.get("USER_MCP_URL", "http://localhost:8086/mcp")
    client = MultiServerMCPClient({
        "Recipe Server": {
            "transport": "http",
            "url": recipe_mcp_url,
        },
        "User Server": {
            "transport": "http",
            "url": user_mcp_url,
        }
    })

    tools = await client.get_tools()

    recipe_agent = create_agent(
        "gpt-4.1-mini",
        tools=tools,
        system_prompt=DISCOVER_RECIPES_SYSTEM_PROMPT,
        response_format=RecipeResult,
    )
   
    yield {"recipe_agent": recipe_agent}

app = FastAPI(lifespan=lifespan)
app.include_router(discovery_routes.router)
