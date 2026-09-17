# recipe-embedding-service

This microservice listens to `recipe-log` Kafka topic and consumes Recipe events. Then it embeds the `Recipe`s using embedding model(`text-embedding-3-large`) and stores the vectors in Qdrant.

The service exposes REST endpoint to retrieve `Recipe`s by ingredient-similarity search. The endpoint is consumed by [recipe-mcp-server](../recipe-mcp-server).

Search is restricted to the given `user_id` (via a Qdrant metadata filter). It returns at most `TOP_K = 2` matches, and only above `SCORE_THRESHOLD = 0.35` cosine similarity. If no sufficiently similar recipe was found then it returns an empty list.

## Tech stack

- **Framework:** FastAPI + uvicorn, Langchain
- **Messaging:** Kafka (via aiokafka)
- **Embeddings:** `text-embedding-3-large` (OpenAI)
- **Vector store:** Qdrant
- **Validation:** Pydantic

## How To Run

### Prerequisites

- Python 3.12+
- A running Kafka broker (with the `recipe-created` topic produced by recipe-service)
- A running Qdrant instance
- An OpenAI API key

### Run Locally

- Export `KAFKA_BOOTSTRAP_SERVERS`, `QDRANT_URL`, `OPENAI_API_KEY` or set via a `.env` file in this directory (loaded by `python-dotenv`) or as an environment variable.

```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export QDRANT_URL=http://localhost:6333
export OPENAI_API_KEY=...

pip install -r requirements.txt
uvicorn main:app --reload --port 8083
```

- The `recipes` collection and its `metadata.user_id` index are created automatically on
import (`database.py`) if they don't already exist.

### Run With Docker

```bash
docker build -t recipe-embedding-service .
docker run -p 8083:8083 \
  --env KAFKA_BOOTSTRAP_SERVERS=host.docker.internal:9092 \
  --env QDRANT_URL=http://host.docker.internal:6333 \
  --env OPENAI_API_KEY=... \
  recipe-embedding-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up recipe-embedding-service kafka qdrant
```

- When run through the root `docker-compose.yml`, all three environment variables are injected automatically.

## API Reference

- Swagger UI: `http://localhost:8083/docs`
- Qdrant UI: `http://localhost:6333/dashboard`

## Known Clients

- Consumed downstream by [recipe-mcp-server](../recipe-mcp-server) (MCP tool
  `get_recipe_by_ingredient`) on behalf of [discovery-agent-service](../discovery-agent-service).
