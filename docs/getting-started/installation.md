# Installation

??? info "AI Summary"

    Run with **uvx** (`uvx dota2-match-analysis@latest`) or **Docker** (`docker run --pull=always dbcjuanma/mcp_replay_dota2`). The `@latest` and `--pull=always` flags ensure you always get the most recent version. Git clone only needed for contributors.

## Option 1: uvx (Recommended)

Run the server directly without installation:

```bash
uvx dota2-match-analysis@latest
```

The `@latest` suffix ensures you always get the most recent version from PyPI.

!!! tip "Why @latest?"
    Without `@latest`, uvx caches the first version it downloads. Using `@latest` ensures you always pull the newest release automatically.

## Option 2: Docker

Run with SSE transport (recommended for Docker):

```bash
docker run --pull=always -p 8081:8081 dbcjuanma/mcp_replay_dota2 --transport sse
```

The `--pull=always` flag ensures Docker always pulls the latest image before running.

See [Docker Guide](docker.md) for persistent cache, STDIO mode, and compose examples.

## Option 3: From Source (Contributors)

Only needed if you want to contribute to the project:

```bash
git clone https://github.com/DeepBlueCoding/mcp-replay-dota2.git
cd mcp-replay-dota2
uv sync
uv run python dota_match_mcp_server.py
```

See [Development Guide](development.md) for testing and contributing.

## Verify Installation

You should see output like:

```
Dota 2 Match MCP Server starting...
Resources: dota2://heroes/all, dota2://map, ...
Tools: get_hero_deaths, get_combat_log, ...
```

## Next Step

[Connect to your LLM](../integrations/index.md)
