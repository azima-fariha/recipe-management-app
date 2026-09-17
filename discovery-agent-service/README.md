
# discovery-agent-service

This is an agentic solution in the `recipe-management-app` system. Given a user and a free-text ingredient query, the agent either returns one of the
user's existing recipes or invents a new one that fits both the ingredients and the user's dietary preferences.

## Agentic Behavior

### MCP

The agent uses two MCP servers() to complete its task:

1.`recipe-mcp-server`: Given `user_id` and list of `ingredient`s, the agent checks if the user already has existing recipe that can be made with the given ingredients using `recipe-mcp-server`. If recipe found then the exact recipe if returned to the user.
2.`user-mcp-server`: Otherwise the agent fetches the user's `preferences` and `dietary_restrictions` using  `user-mcp-server`. Then it invents a new recipe fitting both the ingredients and those pre-set user preferences.

### Guardrails

This service implements basic prompt-based guardrails:

- Always use the `user_id` passed in via the request and never one mentioned inside the free-text query, even if asked to.
- Reject requests with ingredients that aren't real, or that ask for anything other than finding a recipe (including harmful/suspicious requests).

## Tech Stack

- **Framework:** FastAPI + uvicorn, LangChain, LangGraph
- **LLM:** `gpt-4.1-mini`
- **MCP** Multi-Server MCP Client (via `langchain-mcp-adapters`)
- **Structured Output:** Pydantic

## How To Run

### Prerequisites

- Python 3.12+
- `recipe-mcp-server` and `user-mcp-server` running and reachable
- An OpenAI API key

### Run Locally

- Export `OPENAI_API_KEY`, `RECIPE_MCP_URL`, `USER_MCP_URL` or set via a `.env` file in this directory (loaded by `python-dotenv`) or as an environment variable.

```bash
export OPENAI_API_KEY=...
export RECIPE_MCP_URL=http://localhost:8085/mcp
export USER_MCP_URL=http://localhost:8086/mcp

pip install -r requirements.txt
uvicorn main:app --reload --port 8084
```

### Run With Docker

```bash
docker build -t discovery-agent-service .
docker run -p 8084:8084 \
  --env OPENAI_API_KEY=... \
  --env RECIPE_MCP_URL=http://host.docker.internal:8085/mcp \
  --env USER_MCP_URL=http://host.docker.internal:8086/mcp \
  discovery-agent-service
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up discovery-agent-service recipe-mcp-server user-mcp-server
```

- When run through the root `docker-compose.yml`, these environment variables are injected automatically and points at the `mysql` container.

## API Reference

Swagger UI: `http://localhost:8084`

## Known Clients

- [consumer-api](../consumer-api)
