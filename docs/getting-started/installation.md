# Installation

??? info "AI Summary"

    Install from **PyPI** (`uv add mcp-replay-dota2`) or **DockerHub** (`docker pull dbcjuanma/mcp_replay_dota2`). Git clone only needed for contributors.

## Option 1: PyPI (Recommended)

Install the package directly from PyPI:

```bash
# Using uv (recommended)
uv add mcp-replay-dota2

# Or using pip
pip install mcp-replay-dota2
```

Run the server:

```bash
# Using uv
uv run mcp-replay-dota2

# Or directly if installed with pip
mcp-replay-dota2
```

## Option 2: Docker

Pull the image from DockerHub:

```bash
docker pull dbcjuanma/mcp_replay_dota2
```

Run with SSE transport (recommended for Docker):

```bash
docker run -p 8081:8081 dbcjuanma/mcp_replay_dota2 --transport sse
```

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
