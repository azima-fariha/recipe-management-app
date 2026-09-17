# recipe-mcp-server

This MCP server exposes ingredient-based recipe search as an MCP tool, so agents can look up a user's existing recipes by ingredient similarity without knowing about
[recipe-embedding-service](../recipe-embedding-service)'s REST API directly.

## Tech stack

- **Framework:** FastMCP
- **HTTP client:** `requests` (sync)

## How To Run

### Prerequisites

- Python 3.12+
- `recipe-embedding-service` running and reachable

### Run Locally

```bash
pip install -r requirements.txt
python recipe-server.py
```

### Run With Docker

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

## MCP Tool Reference

- Served at `http://localhost:8085/mcp` (streamable-HTTP transport).
- The tool does no error handling of its own — on an unsuccessful response (e.g. a 404), it simply forwards `recipe-embedding-service`'s JSON body as-is to the calling Agent.
- To test the mcp in isolation:
  - Run this command: `npx @modelcontextprotocol/inspector`.
  - This should open a local web UI.
  - Set Transport Type to `Streamable HTTP`.
  - Set URL to `http://localhost:8085/mcp`.
  - Then connect.
  - You'll see the exposed tool (`get_recipe_by_ingredient`) listed, and can invoke it directly with a test `user_id` and `ingredients`, inspect the raw request/response, without needing `discovery-agent-service`.

## Known Clients

- It is used by [discovery-agent-service](../discovery-agent-service) to check for an existing recipe matching by ingredient for a given user, before inventing a new one.
