# user-service

This microservice is responsible for managing the lifecycle of `User` in the platform. Users can also save their dietary restrictions and preferences. This information is used by the `discovery-agent-service` while recommending recipes to the users.

## Tech Stack

- **Framework:** FastAPI + uvicorn
- **Validation:** Pydantic
- **ORM:** SQLAlchemy
- **Database:** MySQL via PyMySQL

## How To Run

### Prerequisites

- Python 3.12+
- A running MySQL instance

### Run Locally

- Export `DATABASE_URL` or set via a `.env` file in this directory (loaded by `python-dotenv`) or as an environment variable.

```bash
export DATABASE_URL=mysql+pymysql://root:password@localhost:3306/recipe_user_db
pip install -r requirements.txt
uvicorn main:app --reload --port 8081
```

- The service creates the `users` table automatically on startup (`Base.metadata.create_all`) if it doesn't already exist.

### Run With Docker

```bash
docker build -t user-service .
docker run -p 8081:8081 --env DATABASE_URL=mysql+pymysql://root:password@host.docker.internal:3306/recipe_user_db user-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up user-service mysql
```

- When run through the root `docker-compose.yml`, `DATABASE_URL` is injected
automatically and points at the `mysql` container.

## API Reference

- Swagger API: `http://localhost:8081/docs`
- `PUT /user/{user_id}` accepts a partial `UserUpdateDto` (`full_name` `dietary_restrictions`, `preferences`). Only the fields present in the request body are updated.

## Known Clients

- This is an internal service.
- [consumer-api](../consumer-api) (public gateway).
- [user-mcp-server](../user-mcp-server) which reads user data and makes it available for the discovery agent.
