# User Service

FastAPI microservice responsible for user CRUD - profile info, dietary restrictions, and
preferences — backed by MySQL. It is one of the internal services in the
[recipe-management-app](../README.md) platform and is normally reached through
[consumer-api](../consumer-api), though it can also be called directly.

## Tech stack

- **Framework:** FastAPI + uvicorn
- **Validation:** Pydantic (`EmailStr`, DTOs)
- **ORM:** SQLAlchemy (declarative models, session-per-request)
- **Database:** MySQL via PyMySQL
- **Config:** python-dotenv
- **Packaging:** Docker

## Project structure

```
user-service/
├── main.py              # FastAPI app entrypoint; wires up the router
├── user_routes.py        # Controller layer — API routes (GET/POST/PUT /user)
├── user_repository.py    # Data access layer — DB queries via SQLAlchemy session
├── models.py              # SQLAlchemy ORM model (User)
├── schemas.py             # Pydantic DTOs (UserDto, UserUpdateDto)
├── database.py            # Engine/session setup, get_db dependency
├── requirements.txt
├── Dockerfile
└── .env                   # DATABASE_URL (not committed in production)
```

The service follows a layered structure:

| Layer | File | Responsibility |
|---|---|---|
| Controller | [user_routes.py](user_routes.py) | Defines the `APIRouter` (`router`) and HTTP endpoints (`get_user`, `create_user`, `update_user`); parses/validates requests via the schema layer, calls the repository directly, raises `HTTPException` on not-found |
| Repository | [user_repository.py](user_repository.py) | Data access layer — `get_user_by_id`, `create_user`, `update_user`; issue queries and writes against the SQLAlchemy `Session` |
| Model / Entity | [models.py](models.py) | SQLAlchemy ORM entity (`User`) mapped to the `users` table |
| Schema / DTO | [schemas.py](schemas.py) | Pydantic request/response DTOs (`UserDto`, `UserUpdateDto`) used at the controller boundary |
| Database config | [database.py](database.py) | Engine creation, session factory, and the `get_db` FastAPI dependency injected into the controller |

Request flow: **Controller → Repository → Database**, with **Schemas** validating data in/out
at the controller boundary and the **Model** describing the persisted shape. There is no
separate service layer — the controller calls the repository directly since the logic is
straightforward CRUD.

`main.py` creates the `FastAPI` app and includes the router exposed by `user_routes`:

```python
app.include_router(user_routes.router)
```

## API reference

Base path (direct): `http://localhost:8081`

| Method | Path | Description | Handler |
|---|---|---|---|
| `GET` | `/user/{user_id}` | Fetch a user by id; `404` if not found | `get_user` in `user_routes.py` |
| `POST` | `/user` | Create a new user | `create_user` in `user_routes.py` |
| `PUT` | `/user/{user_id}` | Update an existing user's mutable fields; `404` if not found | `update_user` in `user_routes.py` |

### User fields

| Field | Type | Notes |
|---|---|---|
| `id` | int | Primary key, auto-increment |
| `full_name` | string | |
| `email` | string | Unique, validated as an email address |
| `created_at` | datetime | Server-set on insert |
| `dietary_restrictions` | string | Optional, free text |
| `preferences` | string | Optional, free text |

`PUT /user/{user_id}` accepts a partial `UserUpdateDto` (`full_name`, `dietary_restrictions`,
`preferences`) — only fields present in the request body are updated.

Interactive OpenAPI docs are available at `/docs` once the service is running.

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy MySQL connection string | `mysql+pymysql://root:password@localhost:3306/recipe_user_db` |

Set via a `.env` file in this directory (loaded by `python-dotenv`) or as an environment
variable. When run through the root `docker-compose.yml`, `DATABASE_URL` is injected
automatically and points at the `mysql` container.

## Getting started

### Prerequisites

- Python 3.12+
- A running MySQL instance

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=mysql+pymysql://root:password@localhost:3306/recipe_user_db
uvicorn main:app --reload --port 8081
```

The service creates the `users` table automatically on startup (`Base.metadata.create_all`)
if it doesn't already exist.

### Run with Docker

```bash
docker build -t user-service .
docker run -p 8081:8081 --env DATABASE_URL=mysql+pymysql://root:password@host.docker.internal:3306/recipe_user_db user-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up user-service mysql
```

## Notes

- The service is stateless; all persistence goes through MySQL.
- Consumed downstream by [consumer-api](../consumer-api) (public gateway) and
  [user-mcp-server](../user-mcp-server) (MCP tool `get_user_by_id` for the discovery agent).
