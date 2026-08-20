# Consumer API

FastAPI microservice that acts as the public API gateway for the platform: it is the only
service a client talks to, proxying requests to [user-service](../user-service),
[recipe-service](../recipe-service), and [discovery-agent-service](../discovery-agent-service)
over HTTP. It is part of the [recipe-management-app](../README.md) platform.

## Tech stack

- **Framework:** FastAPI + uvicorn
- **HTTP client:** httpx (async, shared client per app lifetime)
- **Validation:** Pydantic (`EmailStr`, DTOs)
- **Packaging:** Docker

## Project structure

```
consumer-api/
├── main.py                # FastAPI app entrypoint; lifespan owns a shared httpx.AsyncClient
├── config.py                # Downstream service base URLs
├── recipe_routes.py        # Controller layer — recipe endpoints, proxies to recipe-service
├── recipe_api.py             # Client layer — HTTP calls to recipe-service
├── user_routes.py              # Controller layer — user endpoints, proxies to user-service
├── user_api.py                   # Client layer — HTTP calls to user-service
├── agent_routes.py                 # Controller layer — discovery endpoint, proxies to discovery-agent-service
├── agent_api.py                      # Client layer — HTTP calls to discovery-agent-service
├── schemas.py                          # Pydantic DTOs shared across all three domains
├── requirements.txt
└── Dockerfile
```

The service is a thin proxy: each domain (recipes, users, agent/discovery) has a matching
controller/client pair, all sharing one `httpx.AsyncClient` created in `main.py`'s lifespan
and injected via `request.state.http_client`.

| Domain | Controller | Client | Downstream service |
|---|---|---|---|
| Recipes | [recipe_routes.py](recipe_routes.py) | [recipe_api.py](recipe_api.py) | [recipe-service](../recipe-service) (`RECIPE_SERVICE_URL`) |
| Users | [user_routes.py](user_routes.py) | [user_api.py](user_api.py) | [user-service](../user-service) (`USER_SERVICE_URL`) |
| Discovery / agent | [agent_routes.py](agent_routes.py) | [agent_api.py](agent_api.py) | [discovery-agent-service](../discovery-agent-service) (`AGENT_SERVICE_URL`) |

`config.py` centralizes the recipe/user service URLs as module constants
(`RECIPE_SERVICE_URL`, `USER_SERVICE_URL`); `agent_api.py` reads `AGENT_SERVICE_URL`
directly since discovery is single-purpose.

Request flow: **Controller → Client (`*_api.py`) → downstream service**, with **Schemas**
validating/shaping data in and out at the controller boundary. `recipe_routes.py` translates
`httpx.HTTPStatusError` into a matching `HTTPException` so a downstream 404/403/etc. is
passed through to the caller with its original status code and body; `user_routes.py` and
`agent_routes.py` currently do not (see Notes).

`main.py` creates the `FastAPI` app, opens one shared `httpx.AsyncClient` for the app's
lifetime (closed on shutdown), and includes all three routers:

```python
app.include_router(recipe_routes.router)
app.include_router(user_routes.router)
app.include_router(agent_routes.router)
```

## API reference

Base path (direct): `http://localhost:8088`

| Method | Path | Description | Handler | Proxies to |
|---|---|---|---|---|
| `GET` | `/user/{user_id}` | Fetch a user by id | `get_user` in `user_routes.py` | user-service `GET /user/{user_id}` |
| `POST` | `/user` | Create a new user | `create_user` in `user_routes.py` | user-service `POST /user` |
| `PUT` | `/user/{user_id}` | Update a user's mutable fields | `update_user` in `user_routes.py` | user-service `PUT /user/{user_id}` |
| `GET` | `/user/{user_id}/recipe/{recipe_id}` | Fetch a recipe by id | `fetch_recipe` in `recipe_routes.py` | recipe-service `GET .../recipe/{recipe_id}` |
| `POST` | `/user/{user_id}/recipe` | Create a new recipe | `create_recipe` in `recipe_routes.py` | recipe-service `POST .../recipe` |
| `PUT` | `/user/{user_id}/recipe/{recipe_id}` | Update a recipe's mutable fields | `update_recipe` in `recipe_routes.py` | recipe-service `PUT .../recipe/{recipe_id}` |
| `DELETE` | `/user/{user_id}/recipe/{recipe_id}` | Delete a recipe | `delete_recipe` in `recipe_routes.py` | recipe-service `DELETE .../recipe/{recipe_id}` |
| `POST` | `/user/{user_id}/inspiration` | Find or invent a recipe from a free-text ingredient query | `discover_recipe` in `agent_routes.py` | discovery-agent-service `POST .../discover-recipes` |

Interactive OpenAPI docs are available at `/docs` once the service is running.

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `RECIPE_SERVICE_URL` | Base URL of recipe-service | `http://localhost:8082` |
| `USER_SERVICE_URL` | Base URL of user-service | `http://localhost:8081` |
| `AGENT_SERVICE_URL` | Base URL of discovery-agent-service | `http://localhost:8084` |

All three have local defaults, so the service also runs standalone without an `.env` file.
When run through the root `docker-compose.yml`, all three are injected automatically and
point at the corresponding containers.

## Getting started

### Prerequisites

- Python 3.12+
- user-service, recipe-service, and discovery-agent-service running and reachable

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export RECIPE_SERVICE_URL=http://localhost:8082
export USER_SERVICE_URL=http://localhost:8081
export AGENT_SERVICE_URL=http://localhost:8084
uvicorn main:app --reload --port 8088
```

### Run with Docker

```bash
docker build -t consumer-api .
docker run -p 8088:8088 \
  --env RECIPE_SERVICE_URL=http://host.docker.internal:8082 \
  --env USER_SERVICE_URL=http://host.docker.internal:8081 \
  --env AGENT_SERVICE_URL=http://host.docker.internal:8084 \
  consumer-api
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up consumer-api
```

This is the entrypoint for the whole platform — bringing it up pulls in every other service
as a dependency (see [docker-compose.yml](../docker-compose.yml)).

## Notes

- The service is stateless; it holds no data of its own and exists purely to route and shape
  requests for downstream services.
- `user_routes.py` and `agent_routes.py` do not currently catch `httpx.HTTPStatusError` the
  way `recipe_routes.py` does, so a downstream error there surfaces as an unhandled exception
  (500) rather than passing through the original status code.
- This is the only service a client is expected to call directly; every other service in the
  platform is reached through it.
