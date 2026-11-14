# consumer-api

This microservice acts as the public API gateway for the platform. It is the only
service which is exposed to the users and the frontends. It proxys requests to other internal services of the platform, e.g., [user-service](../user-service),
[recipe-service](../recipe-service), and [discovery-agent-service](../discovery-agent-service) etc.

## Tech Stack

- **Framework:** FastAPI + uvicorn
- **HTTP client:** httpx (async, shared client per app lifetime)
- **Validation:** Pydantic (`EmailStr`, DTOs)
- **Auth:** PyJWT — mints and verifies the Access Token (see root `GLOSSARY.md`)
- **Packaging:** Docker

## Authentication & Ownership

- `consumer-api` owns the Access Token entirely: it mints the token (on signup and on `/auth/login`) and verifies it on every route with a `user_id` in its path. `user-service` never sees or creates a token.
- `POST /auth/login` takes `{email, password}`, calls `user-service`'s internal credential-verification endpoint, and returns a token + the user on success, or 401 on failure.
- `POST /user` (signup) mints a token too, so signing up logs you in immediately.
- Every route with `user_id` in the path requires `Authorization: Bearer <token>`: 401 if missing/invalid/expired, 403 if the token's subject doesn't match the path's `user_id` (Ownership — see root `GLOSSARY.md`).
- The signing secret is `JWT_SECRET_KEY` (see below) — same pattern as `OPENAI_API_KEY` elsewhere in this repo.

## How To Run

### Prerequisites

- Python 3.12+
- `user-service`, `recipe-service`, and `discovery-agent-service` running and reachable

### Run Locally

```bash
export RECIPE_SERVICE_URL=http://localhost:8082
export USER_SERVICE_URL=http://localhost:8081
export AGENT_SERVICE_URL=http://localhost:8084
export JWT_SECRET_KEY=some-long-random-string

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
  --env JWT_SECRET_KEY=some-long-random-string \
  consumer-api
```

### Run Tests

```bash
pip install -r requirements.txt
pytest
```

- `TestClient` against the FastAPI app; downstream calls to `user-service`, `recipe-service`, and `discovery-agent-service` are mocked with `respx` — no other services need to be running.

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up consumer-api
```

- This is the entrypoint for the whole platform — bringing it up pulls in every other service as a dependency (see [docker-compose.yml](../docker-compose.yml)).

## API Reference

Swagger UI: `http://localhost:8088/docs`
