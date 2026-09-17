# consumer-api

This microservice acts as the public API gateway for the platform. It is the only
service which is exposed to the users and the frontends. It proxys requests to other internal services of the platform, e.g., [user-service](../user-service),
[recipe-service](../recipe-service), and [discovery-agent-service](../discovery-agent-service) etc.

## Tech Stack

- **Framework:** FastAPI + uvicorn
- **HTTP client:** httpx (async, shared client per app lifetime)
- **Validation:** Pydantic (`EmailStr`, DTOs)
- **Packaging:** Docker

## How To Run

### Prerequisites

- Python 3.12+
- `user-service`, `recipe-service`, and `discovery-agent-service` running and reachable

### Run Locally

```bash
export RECIPE_SERVICE_URL=http://localhost:8082
export USER_SERVICE_URL=http://localhost:8081
export AGENT_SERVICE_URL=http://localhost:8084

pip install -r requirements.txt
uvicorn main:app --reload --port 8088
```

### Run With Docker

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

- This is the entrypoint for the whole platform — bringing it up pulls in every other service as a dependency (see [docker-compose.yml](../docker-compose.yml)).

## API Reference

Swagger UI: `http://localhost:8088/docs`
