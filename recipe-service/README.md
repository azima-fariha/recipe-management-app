# Recipe Service

FastAPI microservice responsible for recipe CRUD — name, ingredients, and instructions —
backed by MongoDB, publishing create/update/delete events to Kafka for downstream embedding.
It is one of the internal services in the [recipe-management-app](../README.md) platform and
is normally reached through [consumer-api](../consumer-api), though it can also be called
directly.

## Tech stack

- **Framework:** FastAPI + uvicorn
- **Validation:** Pydantic (DTOs)
- **ODM:** Beanie (async, over Motor/PyMongo)
- **Database:** MongoDB via `AsyncMongoClient`
- **Messaging:** Kafka via aiokafka (producer only)
- **Packaging:** Docker

## Project structure

```
recipe-service/
├── main.py                # FastAPI app entrypoint; lifespan (DB init, Kafka producer), router, error handler
├── recipe_routes.py       # Controller layer — API routes (GET/POST/PUT/DELETE /user/{user_id}/recipe)
├── recipe_service.py      # Service layer — ownership checks, partial updates, orchestration
├── recipe_repository.py   # Data access layer — Beanie/MongoDB queries
├── mapper.py               # Model <-> DTO conversion (Recipe <-> RecipeDto)
├── models.py                # Beanie Document model (Recipe)
├── schemas.py               # Pydantic DTOs (RecipeDto, RecipeUpdateDto, RecipeCreatedEvent)
├── exceptions.py             # AppError hierarchy (NotFoundError, ForbiddenError) + status codes
├── kafka_producer.py          # Publishes recipe create/update/delete events to Kafka
├── database.py                 # Mongo client + Beanie initialization
├── requirements.txt
└── Dockerfile
```

The service follows a layered structure:

| Layer | File | Responsibility |
|---|---|---|
| Controller | [recipe_routes.py](recipe_routes.py) | Defines the `APIRouter` (`router`) and HTTP endpoints (`get_recipe`, `create_recipe`, `update_recipe`, `delete_recipe`); delegates to the service layer, maps models to DTOs via `mapper`, and publishes Kafka events after writes |
| Service | [recipe_service.py](recipe_service.py) | Business logic — `get_recipe_by_id` (raises `NotFoundError`/`ForbiddenError`), `create_recipe`, `update_recipe` (applies only the fields present on `RecipeUpdateDto`), `delete_recipe` |
| Repository | [recipe_repository.py](recipe_repository.py) | Data access layer — `get_recipe_by_id`, `create_recipe`, `update_recipe`, `delete_recipe`; thin wrapper over Beanie's `Recipe.get/insert/save/delete` |
| Mapper | [mapper.py](mapper.py) | Converts between the `Recipe` document and `RecipeDto` (`to_dto`, `to_model`) |
| Model / Document | [models.py](models.py) | Beanie `Document` (`Recipe`) mapped to the `recipes` collection |
| Schema / DTO | [schemas.py](schemas.py) | Pydantic request/response DTOs (`RecipeDto`, `RecipeUpdateDto`) and the Kafka event payload (`RecipeCreatedEvent`) |
| Exceptions | [exceptions.py](exceptions.py) | `AppError` base class plus `NotFoundError` (404) and `ForbiddenError` (403), translated to HTTP responses by a global exception handler in `main.py` |
| Kafka producer | [kafka_producer.py](kafka_producer.py) | `publish_event` / `publish_deletion_event` — sends recipe events (or a tombstone on delete) to the `recipe-created` topic |
| Database config | [database.py](database.py) | Mongo client, database handle, and `init_db` (Beanie initialization) called from the app lifespan |

Request flow: **Controller → Service → Repository → Database**, with the **Mapper**
converting between the persisted `Recipe` document and the `RecipeDto` at the controller
boundary, and the **Controller** publishing a Kafka event after any successful write so
downstream consumers (recipe-embedding-service) stay in sync.

`main.py` wires the app together via a lifespan context manager: it calls `init_db()` on
startup, starts a shared `AIOKafkaProducer` (stopped on shutdown), and stashes it on
`request.state.kafka_producer` for the routes to use. It also registers an exception handler
that turns any `AppError` into a JSON `{"reason": ...}` response with the error's status code.

```python
app.include_router(recipe_routes.router)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, ex: AppError):
    return JSONResponse(status_code=ex.status_code, content={"reason": ex.reason})
```

## API reference

Base path (direct): `http://localhost:8082`

| Method | Path | Description | Handler |
|---|---|---|---|
| `GET` | `/user/{user_id}/recipe/{recipe_id}` | Fetch a recipe by id; `404` if not found, `403` if it belongs to another user | `get_recipe` in `recipe_routes.py` |
| `POST` | `/user/{user_id}/recipe` | Create a new recipe for the user; publishes a `recipe-created` event | `create_recipe` in `recipe_routes.py` |
| `PUT` | `/user/{user_id}/recipe/{recipe_id}` | Update an existing recipe's mutable fields; publishes a `recipe-created` event | `update_recipe` in `recipe_routes.py` |
| `DELETE` | `/user/{user_id}/recipe/{recipe_id}` | Delete a recipe; publishes a tombstone (`null` value) event; returns `204` | `delete_recipe` in `recipe_routes.py` |

### Recipe fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | MongoDB ObjectId, string-encoded; server-set on insert |
| `name` | string | |
| `ingredients` | string[] | |
| `instructions` | string | |
| `user_id` | string | Owning user's id; taken from the path, not the request body |

`PUT /user/{user_id}/recipe/{recipe_id}` accepts a partial `RecipeUpdateDto` (`name`,
`ingredients`, `instructions`) — only fields present in the request body are updated.

Every route enforces ownership: `recipe_service.get_recipe_by_id` raises `ForbiddenError`
(403) if the recipe's `user_id` doesn't match the `user_id` in the path.

Interactive OpenAPI docs are available at `/docs` once the service is running.

## Kafka events

On create/update, the service publishes a `RecipeCreatedEvent` to the `recipe-created` topic,
keyed by recipe id:

```json
{
  "id": "...",
  "name": "...",
  "ingredients": ["..."],
  "instructions": "...",
  "user_id": "..."
}
```

On delete, it publishes a tombstone (`value=None`) with the same key so log-compacted topics
drop the record. [recipe-embedding-service](../recipe-embedding-service) consumes this topic
to keep its vector index in sync.

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address(es) | `localhost:9092` |

Both have local defaults (`localhost:27017` / `localhost:9092`) so the service also runs
without a `.env` file. When run through the root `docker-compose.yml`, both variables are
injected automatically and point at the `mongodb` and `kafka` containers.

## Getting started

### Prerequisites

- Python 3.12+
- A running MongoDB instance
- A running Kafka broker

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export MONGO_URL=mongodb://localhost:27017
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
uvicorn main:app --reload --port 8082
```

The `recipes` collection and its Beanie indexes are initialized automatically on startup
(`init_beanie`) if they don't already exist.

### Run with Docker

```bash
docker build -t recipe-service .
docker run -p 8082:8082 \
  --env MONGO_URL=mongodb://host.docker.internal:27017 \
  --env KAFKA_BOOTSTRAP_SERVERS=host.docker.internal:9092 \
  recipe-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up recipe-service mongodb kafka
```

## Notes

- The service is stateless aside from the shared Kafka producer held on `app.state`; all
  persistence goes through MongoDB.
- Consumed downstream by [consumer-api](../consumer-api) (public gateway) and, indirectly via
  Kafka, by [recipe-embedding-service](../recipe-embedding-service), which embeds recipe text
  and upserts it into Qdrant for [recipe-mcp-server](../recipe-mcp-server)'s
  ingredient-similarity search.
