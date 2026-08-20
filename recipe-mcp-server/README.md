# Recipe MCP Server

FastMCP server that exposes ingredient-based recipe search as an MCP tool, so LLM agents can
look up a user's existing recipes by ingredient similarity without knowing about
[recipe-embedding-service](../recipe-embedding-service)'s REST API directly. It is part of
the [recipe-management-app](../README.md) platform and is used as a tool server by
[discovery-agent-service](../discovery-agent-service).

## Tech stack

- **Framework:** [FastMCP](https://github.com/jlowin/fastmcp) (streamable-HTTP transport)
- **HTTP client:** `requests` (sync)
- **Packaging:** Docker

## Project structure

```
recipe-mcp-server/
├── recipe-server.py      # MCP server definition + the get_recipe_by_ingredient tool
├── requirements.txt
└── Dockerfile
```

This is a single-file service — there's no layered controller/repository split like the REST
services, since its entire job is to wrap one downstream HTTP call as one MCP tool.

| File | Responsibility |
|---|---|
| [recipe-server.py](recipe-server.py) | Creates the `FastMCP` app (`"Recipe Server"`), defines the `get_recipe_by_ingredient` tool, and runs the server over streamable-HTTP on startup |

## MCP tool reference

| Tool | Args | Description |
|---|---|---|
| `get_recipe_by_ingredient` | `user_id: str`, `ingredients: str` | Calls `POST {RECIPE_EMBEDDING_SERVICE_URL}/user/{user_id}/recipe-by-ingredients` with `{"ingredientRequest": ingredients}` and returns the JSON list of matching recipes as-is |

An empty list means recipe-embedding-service found no sufficiently similar recipe for that
user (see its `SCORE_THRESHOLD`); the tool does no error handling or filtering of its own.

Served at `http://localhost:8085/mcp` (streamable-HTTP transport).

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `RECIPE_EMBEDDING_SERVICE_URL` | Base URL of recipe-embedding-service | `http://localhost:8083` |

Has a local default, so the service also runs standalone without extra configuration. When
run through the root `docker-compose.yml`, it's injected automatically and points at the
`recipe-embedding-service` container.

## Getting started

### Prerequisites

- Python 3.12+
- recipe-embedding-service running and reachable

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export RECIPE_EMBEDDING_SERVICE_URL=http://localhost:8083
python recipe-server.py
```

### Run with Docker

```bash
docker build -t recipe-mcp-server .
docker run -p 8085:8085 \
  --env RECIPE_EMBEDDING_SERVICE_URL=http://host.docker.internal:8083 \
  recipe-mcp-server
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up recipe-mcp-server recipe-embedding-service kafka qdrant
```

## Notes

- The service is stateless; it holds no data of its own and exists purely to expose
  recipe-embedding-service's similarity search as an MCP tool.
- Consumed by [discovery-agent-service](../discovery-agent-service), which wires this server
  in via `MultiServerMCPClient` (`RECIPE_MCP_URL`) and uses `get_recipe_by_ingredient` to
  check for an existing matching recipe before inventing a new one. Compare with
  [user-mcp-server](../user-mcp-server), the analogous wrapper for user lookup.
