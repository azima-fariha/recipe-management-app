# user-mcp-server

This MCP server exposes user lookup as an MCP tool, so Agents can look up a user's profile and dietary preferences without knowing about [user-service](../user-service)'s REST API directly.

## Tech stack

- **Framework:** FastMCP
- **HTTP client:** `requests` (sync)

## How To Run

### Prerequisites

- Python 3.12+
- `user-service` running and reachable

### Run Locally

```bash
pip install -r requirements.txt
python user-server.py
```

### Run With Docker

```bash
docker build -t user-mcp-server .
docker run -p 8086:8086 \
  --env USER_SERVICE_URL=http://host.docker.internal:8081 \
  user-mcp-server
```

Or, from the repo root, run it as part of the full stack:

```bash
docker compose up user-mcp-server user-service mysql
```

## MCP Tool Reference

- Served at `http://localhost:8086/mcp` (streamable-HTTP transport).
- The tool does no error handling of its own. On an unsuccessful response (e.g. a 404), it simply forwards `user-service`'s JSON body as-is to the calling Agent.
- To test the mcp in isolation:
  - Run this command: `npx @modelcontextprotocol/inspector`.
  - This should open a local web UI.
  - Set Transport Type to `Streamable HTTP`.
  - Set URL to `http://localhost:8086/mcp`.
  - Then connect.
  - You'll see the exposed tool (`get_user_by_id`) listed, and can invoke it directly with a test `user_id`, inspect the raw request/response, without needing `discovery-agent-service`.

## Known Clients

- It is used as a tool server by [discovery-agent-service](../discovery-agent-service) to fetch a user's dietary preferences when inventing a new recipe.
