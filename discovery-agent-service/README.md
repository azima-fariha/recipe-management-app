# Discovery Agent Service

FastAPI microservice that wraps a LangChain agent (`gpt-4.1-mini`) for "find me something to
cook" requests: given a user and a free-text ingredient query, it either returns one of the
user's existing recipes or invents a new one that fits both the ingredients and the user's
dietary preferences. It is one of the internal services in the
[recipe-management-app](../README.md) platform and is normally reached through
[consumer-api](../consumer-api), though it can also be called directly.

## Tech stack

- **Framework:** FastAPI + uvicorn
- **Agent:** LangChain (`create_agent`) + LangGraph, OpenAI `gpt-4.1-mini`
- **Tool access:** MCP via `langchain-mcp-adapters` (`MultiServerMCPClient`, streamable-HTTP)
- **Validation:** Pydantic (structured agent output)
- **Config:** python-dotenv
- **Packaging:** Docker

## Project structure

```
discovery-agent-service/
├── main.py                # FastAPI app entrypoint; lifespan builds the MCP client + agent
├── discovery_routes.py    # Controller layer — API route (POST /user/{user_id}/discover-recipes)
├── prompts.py               # System prompt and the per-request prompt template
├── schemas.py                # Pydantic DTOs (DiscoverRequest, RecipeResult)
├── requirements.txt
├── Dockerfile
└── .env                        # OPENAI_API_KEY (not committed in production)
```

| Component | File | Responsibility |
|---|---|---|
| App wiring | [main.py](main.py) | Lifespan connects to both MCP servers via `MultiServerMCPClient`, fetches their tools, and builds a `create_agent` instance (`gpt-4.1-mini`, structured output `RecipeResult`) once at startup, stashed on `request.state.recipe_agent` |
| Controller | [discovery_routes.py](discovery_routes.py) | Defines the `APIRouter` (`router`) and the `discover_recipes` endpoint; formats the prompt, invokes the agent, and returns its structured response |
| Prompts | [prompts.py](prompts.py) | `DISCOVER_RECIPES_SYSTEM_PROMPT` (agent behavior/guardrails) and `discover_recipes_prompt` (a `ChatPromptTemplate` injecting `user_id` and the user's `query` as a human message) |
| Schema / DTO | [schemas.py](schemas.py) | `DiscoverRequest` (request body: `query`) and `RecipeResult` (agent's structured output: `name`, `ingredients`, `instructions`) |

There is no repository or database layer here — the agent's "tools" are the two MCP servers
wired up in `main.py`'s lifespan:

- **recipe-mcp-server** (`RECIPE_MCP_URL`) — searches the user's existing recipes by
  ingredient similarity (backed by recipe-embedding-service).
- **user-mcp-server** (`USER_MCP_URL`) — looks up the user's dietary preferences (backed by
  user-service).

The agent itself is created once at startup (not per-request) and reused across requests via
FastAPI's lifespan state.

## Agent behavior

The system prompt in [prompts.py](prompts.py) constrains the agent to:

- Always use the `user_id` passed in via the request (never one mentioned inside the free-text
  query, even if asked to).
- Check that an existing recipe from the same user can be made with the given ingredients
  (via the MCP recipe search tool) and return it as-is if found.
- Otherwise fetch the user's preferences (via the MCP user-lookup tool) and invent a new
  recipe — name, ingredients, instructions — fitting both the ingredients and those
  preferences.
- Reject requests with ingredients that aren't real, or that ask for anything other than
  finding a recipe (including harmful/suspicious requests) — but still return exactly one
  `RecipeResult`, with `ingredients` left empty and `instructions` stating the reason.

## API reference

Base path (direct): `http://localhost:8084`

| Method | Path | Description | Handler |
|---|---|---|---|
| `POST` | `/user/{user_id}/discover-recipes` | Find or invent a recipe for the user given a free-text ingredient/preference query | `discover_recipes` in `discovery_routes.py` |

Request body (`DiscoverRequest`):

```json
{ "query": "I have chicken, garlic, and lemon — what can I make?" }
```

Response (`RecipeResult`):

```json
{ "name": "...", "ingredients": ["..."], "instructions": "..." }
```

Interactive OpenAPI docs are available at `/docs` once the service is running.

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key used by the LangChain agent | `sk-...` |
| `RECIPE_MCP_URL` | Streamable-HTTP URL of recipe-mcp-server | `http://localhost:8085/mcp` |
| `USER_MCP_URL` | Streamable-HTTP URL of user-mcp-server | `http://localhost:8086/mcp` |

`RECIPE_MCP_URL` and `USER_MCP_URL` have local defaults; `OPENAI_API_KEY` is loaded from a
`.env` file in this directory via `python-dotenv` (or as an environment variable) and has no
default. When run through the root `docker-compose.yml`, all three are injected automatically
and point at the `recipe-mcp-server` and `user-mcp-server` containers.

## Getting started

### Prerequisites

- Python 3.12+
- recipe-mcp-server and user-mcp-server running and reachable
- An OpenAI API key

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
export RECIPE_MCP_URL=http://localhost:8085/mcp
export USER_MCP_URL=http://localhost:8086/mcp
uvicorn main:app --reload --port 8084
```

### Run with Docker

```bash
docker build -t discovery-agent-service .
docker run -p 8084:8084 \
  --env OPENAI_API_KEY=sk-... \
  --env RECIPE_MCP_URL=http://host.docker.internal:8085/mcp \
  --env USER_MCP_URL=http://host.docker.internal:8086/mcp \
  discovery-agent-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up discovery-agent-service recipe-mcp-server user-mcp-server
```

## Notes

- The service is stateless aside from the agent and MCP client built once at startup; all
  "memory" of a request lives in the single request/response cycle.
- Called by [consumer-api](../consumer-api) (public gateway, `POST /user/{user_id}/inspiration`).
  Calls out to [recipe-mcp-server](../recipe-mcp-server) and
  [user-mcp-server](../user-mcp-server) as agent tools, and to the OpenAI API directly for
  both tool-calling and, when no matching recipe exists, inventing one.
