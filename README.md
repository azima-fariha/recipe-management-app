# Recipe Management App

This is a microservices-based recipe platform. Users manage recipes through a REST gateway, recipe events flow through Kafka into a vector store, and an LLM agent uses MCP tools to discover or invent recipes from a list of ingredients.

## Architecture

![System Design](system-design.jpg)

1. A client talks only to [consumer-api](consumer-api), which proxies requests to the internal services.
2. Creating, updating or deleting a recipe in [recipe-service](recipe-service) publishes an event to the Kafka topic `recipe-log`, keyed by `recipe_id`. A delete publishes a tombstone (`value=None`).
3. [recipe-embedding-service](recipe-embedding-service) consumes that topic, embeds the recipe text with OpenAI (`text-embedding-3-large`), and upserts it into Qdrant.
4. For "find me something to cook" requests, [discovery-agent-service](discovery-agent-service) runs a LangChain agent (`gpt-4.1-mini`) that calls two MCP servers as tools:
   - [recipe-mcp-server](recipe-mcp-server) searches the user's existing recipes by ingredient similarity (via recipe-embedding-service).
   - [user-mcp-server](user-mcp-server) looks up the user's dietary preferences (via user-service).
- If no matching recipe exists, the agent invents one that fits the ingredients and the user's preferences instead of returning nothing.

## Services

| Service | Port | Responsibility | Storage / Dependencies |
|---|---|---|---|
| [consumer-api](consumer-api) | 8088 | Public API gateway; proxies to user, recipe, and discovery services | — |
| [user-service](user-service) | 8081 | User CRUD (profile, dietary restrictions, preferences) | MySQL |
| [recipe-service](recipe-service) | 8082 | Recipe CRUD; publishes create/update/delete events | MongoDB, Kafka (producer) |
| [recipe-embedding-service](recipe-embedding-service) | 8083 | Consumes recipe events, generates embeddings, similarity search | Kafka (consumer), Qdrant, OpenAI |
| [discovery-agent-service](discovery-agent-service) | 8084 | LLM agent that finds or invents a recipe from ingredients | OpenAI, MCP servers |
| [recipe-mcp-server](recipe-mcp-server) | 8085 | MCP tool wrapper: `get_recipe_by_ingredient` | recipe-embedding-service |
| [user-mcp-server](user-mcp-server) | 8086 | MCP tool wrapper: `get_user_by_id` | user-service |

- Each service has its own README with service-specific details.

### Infrastructure

| Component | Role |
|---|---|
| MySQL | User records (`recipe_user_db`) |
| MongoDB | Recipe documents |
| Kafka + Zookeeper | `recipe-log` event stream between recipe-service and recipe-embedding-service |
| Qdrant | Vector store for ingredient-similarity search |

## Tech Stack

- **Framework:** FastAPI + uvicorn
- **Validation:** Pydantic
- **Persistence:** SQLAlchemy + PyMySQL (users), Beanie over MongoDB (recipes), Qdrant (vectors)
- **Messaging:** Kafka via aiokafka
- **AI/Agents:** LangChain, LangGraph, `langchain-mcp-adapters`, OpenAI (`gpt-4.1-mini`, `text-embedding-3-large`)
- **MCP:** FastMCP (streamable-HTTP transport)
- **Packaging:** Docker / Docker Compose, one Dockerfile per service

## How To Run

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (only for running services outside Docker)
- An OpenAI API key (used by `recipe-embedding-service` and `discovery-agent-service`)

### Run With Docker

```bash
export OPENAI_API_KEY=sk-...
docker compose up --build
```

- This starts the infrastructure (MySQL, MongoDB, Kafka/Zookeeper, Qdrant) and all seven application services.
- All URLs and credentials are injected automatically from [docker-compose.yml](docker-compose.yml).

### Run Locally

- Start only the infrastructure containers:

```bash
docker compose up mysql mongodb kafka zookeeper qdrant
```

- Then, from a service directory:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port <service-port>   # or `python <name>-server.py` for the MCP servers
```

- Services read their downstream URLs from environment variables, set via a `.env` file in the service directory or exported in the shell. Most have `localhost`-based defaults.
