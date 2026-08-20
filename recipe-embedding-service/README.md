# Recipe Embedding Service

FastAPI microservice that consumes recipe events from Kafka, embeds their text with OpenAI,
and stores/searches the vectors in Qdrant. It is one of the internal services in the
[recipe-management-app](../README.md) platform. It has no direct-write API of its own — it
is fed entirely by [recipe-service](../recipe-service) via Kafka — and exposes one read
endpoint used by [recipe-mcp-server](../recipe-mcp-server) for ingredient-similarity search.

## Tech stack

- **Framework:** FastAPI + uvicorn
- **Messaging:** Kafka via aiokafka (consumer only)
- **Embeddings:** OpenAI (`text-embedding-3-large`) via `langchain-openai`
- **Vector store:** Qdrant via `langchain-qdrant` / `qdrant-client`
- **Validation:** Pydantic
- **Config:** python-dotenv
- **Packaging:** Docker

## Project structure

```
recipe-embedding-service/
├── main.py             # FastAPI app entrypoint; lifespan starts a background Kafka consumer task
├── vector_routes.py     # Controller layer — search endpoint (POST /user/{user_id}/recipe-by-ingredients)
├── vector_service.py     # Embedding + Qdrant operations (vectorize, search, delete)
├── database.py             # Qdrant client + collection/index bootstrap
├── schemas.py                # Pydantic DTOs (IngredientRequest, RecipeCreatedEvent)
├── requirements.txt
├── Dockerfile
└── .env                        # OPENAI_API_KEY (not committed in production)
```

The service is split into a Kafka-driven ingestion path and an HTTP-driven query path, both
built on the same vector store:

| Component | File | Responsibility |
|---|---|---|
| Kafka consumer | [main.py](main.py) | `consume_recipe_events` — runs as a background task for the app's lifetime; on each message it deletes the vector for tombstones (`value is None`) or validates the payload into a `RecipeCreatedEvent` and vectorizes it |
| Controller | [vector_routes.py](vector_routes.py) | Defines the `APIRouter` (`router`) and the `retrieve_recipe_by_ingredient` endpoint; delegates to `vector_service` |
| Vector service | [vector_service.py](vector_service.py) | `vectorize_recipe`, `retrieve_similar_texts_by_user`, `delete_recipe` — builds embedding text, calls OpenAI via `QdrantVectorStore`, and scopes similarity search to a `user_id` metadata filter |
| Database config | [database.py](database.py) | Qdrant client, creates the `recipes` collection (cosine distance, 3072-dim vectors matching `text-embedding-3-large`) and a keyword index on `metadata.user_id` if they don't already exist |
| Schema / DTO | [schemas.py](schemas.py) | `IngredientRequest` (search body), `RecipeCreatedEvent` (Kafka payload; all fields optional to tolerate partial/legacy events), with `to_embedding_text()` combining name/ingredients/instructions into the text sent to the embedding model |

Both ingestion and query use the same Qdrant collection (`recipes`) and metadata shape
(`recipe_id`, `user_id`), and both key vector point IDs off a deterministic UUID5 derived
from the recipe id (`point_id`) so re-embedding an updated recipe overwrites its existing
point rather than duplicating it.

## Kafka consumption

On startup, `main.py`'s lifespan starts an `AIOKafkaConsumer` subscribed to the
`recipe-created` topic (`group_id="recipe-embedding-service"`, `auto_offset_reset="earliest"`)
and hands it to a background task that runs for the life of the app:

- **Tombstone** (`value is None`, published on recipe delete) → `vector_service.delete_recipe`
  removes the corresponding point from Qdrant.
- **Recipe event** → validated into `RecipeCreatedEvent` and passed to
  `vector_service.vectorize_recipe`, which embeds `to_embedding_text()` and upserts it.
- Messages with a null key are skipped, and any processing exception is logged
  (`logger.exception`) without crashing the consumer loop.

## API reference

Base path (direct): `http://localhost:8083`

| Method | Path | Description | Handler |
|---|---|---|---|
| `POST` | `/user/{user_id}/recipe-by-ingredients` | Find the user's existing recipes similar to a free-text ingredient list | `retrieve_recipe_by_ingredient` in `vector_routes.py` |

Request body (`IngredientRequest`):

```json
{ "ingredientRequest": "chicken, garlic, lemon" }
```

Search is restricted to the given `user_id` (via a Qdrant metadata filter), returns at most
`TOP_K = 2` matches, and only above `SCORE_THRESHOLD = 0.35` cosine similarity — an empty
list means no sufficiently similar recipe was found. This is the endpoint
[recipe-mcp-server](../recipe-mcp-server)'s `get_recipe_by_ingredient` tool calls on behalf
of the discovery agent.

Interactive OpenAPI docs are available at `/docs` once the service is running.

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address(es) to consume from | `localhost:9092` |
| `QDRANT_URL` | Qdrant HTTP endpoint | `http://localhost:6333` |
| `OPENAI_API_KEY` | OpenAI API key used for `text-embedding-3-large` | `sk-...` |

`KAFKA_BOOTSTRAP_SERVERS` and `QDRANT_URL` have local defaults; `OPENAI_API_KEY` is loaded
from a `.env` file in this directory via `python-dotenv` (or as an environment variable) and
has no default. When run through the root `docker-compose.yml`, all three are injected
automatically.

## Getting started

### Prerequisites

- Python 3.12+
- A running Kafka broker (with the `recipe-created` topic produced by recipe-service)
- A running Qdrant instance
- An OpenAI API key

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export QDRANT_URL=http://localhost:6333
export OPENAI_API_KEY=sk-...
uvicorn main:app --reload --port 8083
```

The `recipes` collection and its `metadata.user_id` index are created automatically on
import (`database.py`) if they don't already exist.

### Run with Docker

```bash
docker build -t recipe-embedding-service .
docker run -p 8083:8083 \
  --env KAFKA_BOOTSTRAP_SERVERS=host.docker.internal:9092 \
  --env QDRANT_URL=http://host.docker.internal:6333 \
  --env OPENAI_API_KEY=sk-... \
  recipe-embedding-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up recipe-embedding-service kafka qdrant
```

## Notes

- The service does no writes of its own beyond what the Kafka consumer produces — there is
  no create/update/delete HTTP endpoint; recipe mutations always originate in
  [recipe-service](../recipe-service).
- Consumed downstream by [recipe-mcp-server](../recipe-mcp-server) (MCP tool
  `get_recipe_by_ingredient`) on behalf of [discovery-agent-service](../discovery-agent-service).
