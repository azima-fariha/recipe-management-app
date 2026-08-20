# User MCP Server

FastMCP server that exposes user lookup as an MCP tool, so LLM agents can look up a user's
profile and dietary preferences without knowing about [user-service](../user-service)'s REST
API directly. It is part of the [recipe-management-app](../README.md) platform and is used as
a tool server by [discovery-agent-service](../discovery-agent-service).

## Tech stack

- **Framework:** [FastMCP](https://github.com/jlowin/fastmcp) (streamable-HTTP transport)
- **HTTP client:** `requests` (sync)
- **Packaging:** Docker

## Project structure

```
user-mcp-server/
├── user-server.py      # MCP server definition + the get_user_by_id tool
├── requirements.txt
└── Dockerfile
```

This is a single-file service — there's no layered controller/repository split like the REST
services, since its entire job is to wrap one downstream HTTP call as one MCP tool.

| File | Responsibility |
|---|---|
| [user-server.py](user-server.py) | Creates the `FastMCP` app (`"User Server"`), defines the `get_user_by_id` tool, and runs the server over streamable-HTTP on startup |

## MCP tool reference

| Tool | Args | Description |
|---|---|---|
| `get_user_by_id` | `user_id: str` | Calls `GET {USER_SERVICE_URL}/user/{user_id}` on user-service and returns the JSON response as-is |

The tool does no error handling of its own — a non-2xx response from user-service (e.g. a 404
for an unknown user) is returned to the calling agent as whatever JSON body user-service sent.

Served at `http://localhost:8086/mcp` (streamable-HTTP transport).

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| `USER_SERVICE_URL` | Base URL of user-service | `http://localhost:8081` |

Has a local default, so the service also runs standalone without extra configuration. When
run through the root `docker-compose.yml`, it's injected automatically and points at the
`user-service` container.

## Getting started

### Prerequisites

- Python 3.12+
- user-service running and reachable

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export USER_SERVICE_URL=http://localhost:8081
python user-server.py
```

### Run with Docker

```bash
docker build -t user-mcp-server .
docker run -p 8086:8086 --env USER_SERVICE_URL=http://host.docker.internal:8081 user-mcp-server
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up user-mcp-server user-service mysql
```

## Notes

- The service is stateless; it holds no data of its own and exists purely to expose
  user-service as an MCP tool.
- Consumed by [discovery-agent-service](../discovery-agent-service), which wires this server
  in via `MultiServerMCPClient` (`USER_MCP_URL`) and uses `get_user_by_id` to fetch a user's
  dietary preferences when inventing a new recipe. Compare with
  [recipe-mcp-server](../recipe-mcp-server), the analogous wrapper for recipe search.
