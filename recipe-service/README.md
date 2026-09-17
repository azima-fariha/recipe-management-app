# recipe-service

This microservice is responsible for managing the lifecycle of `Recipe`. It uses MongoDB as database and publishes create/update/delete events to Kafka for downstream services.

## Kafka events

- On create/update, the service publishes a `RecipeCreatedEvent` to the `recipe-log` topic, keyed by `recipe_id`:

```json
{
  "id": "...",
  "name": "...",
  "ingredients": ["..."],
  "instructions": "...",
  "user_id": "..."
}
```

- On delete, it publishes a tombstone (`value=None`) with the same key.
- [recipe-embedding-service](../recipe-embedding-service) consumes this topic
to keep its vector index in sync.

## Tech Stack

- **Framework:** FastAPI + uvicorn
- **Validation:** Pydantic
- **ODM:** Beanie
- **Database:** MongoDB via PyMongo
- **Messaging:** Kafka via aiokafka

## How To Run

### Prerequisites

- Python 3.12+
- A running MongoDB instance
- A running Kafka broker

### Run Locally

- Export `MONGO_URL` and `KAFKA_BOOTSTRAP_SERVERS` or set via a `.env` file in this directory (loaded by `python-dotenv`) or as an environment variable.

```bash
export MONGO_URL=mongodb://localhost:27017
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
pip install -r requirements.txt
uvicorn main:app --reload --port 8082
```

- The `recipes` collection and its Beanie indexes are initialized automatically on startup (`init_beanie`) if they don't already exist.

### Run With Docker

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

- When running through the root `docker-compose.yml`, both variables are
injected automatically and point at the `mongodb` and `kafka` containers.

## API Reference

- Swagger API:: `http://localhost:8082/docs`
- `PUT /user/{user_id}/recipe/{recipe_id}` accepts a partial `RecipeUpdateDto` (`name`, `ingredients`, `instructions`). Only the fields present in the request body are updated.

## Known Clients

- Consumed downstream by [consumer-api](../consumer-api) (public gateway)
- The Kafka events produced by this service is consumed by [recipe-embedding-service](../recipe-embedding-service), which embeds recipe text and upserts it into Qdrant for [recipe-mcp-server](../recipe-mcp-server)'s ingredient-similarity search.
