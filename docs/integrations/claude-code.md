# Claude Code CLI

??? info "AI Summary"

    Add to `.mcp.json` (project) or `~/.claude/settings.json` (global): `{"mcpServers": {"dota2-match-analysis": {"command": "uvx", "args": ["dota2-match-analysis@latest"]}}}`. Verify with `/mcp`. Ask: "Analyze match 8461956309". Can also generate scripts using real match data.

Use the Dota 2 MCP server within Claude Code for development workflows.

## Project-Level Setup

Add to your project's `.mcp.json`:

=== "uvx (Recommended)"

    ```json
    {
      "mcpServers": {
        "dota2-match-analysis": {
          "command": "uvx",
          "args": ["dota2-match-analysis@latest"]
        }
      }
    }
    ```

=== "Docker"

    ```json
    {
      "mcpServers": {
        "dota2-match-analysis": {
          "command": "docker",
          "args": ["run", "--pull=always", "-i", "--rm", "dbcjuanma/mcp_replay_dota2"]
        }
      }
    }
    ```

## Global Setup

Add to `~/.claude/settings.json` to make it available in all projects:

```json
{
  "mcpServers": {
    "dota2-match-analysis": {
      "command": "uvx",
      "args": ["dota2-match-analysis@latest"]
    }
  }
}
```

!!! tip "Why @latest?"
    The `@latest` suffix ensures uvx always downloads the newest version from PyPI. Without it, uvx caches the first version it downloads.

## Verify

Run Claude Code and check available tools:

```bash
claude
> /mcp
```

You should see the Dota 2 tools listed.

## Usage

In any Claude Code session:

```
> Analyze match 8461956309 and tell me about the first blood
```

Claude will use the MCP tools automatically.

## Use Case: Replay Analysis Scripts

You can ask Claude Code to write scripts that use match data:

```
> Write a Python script that analyzes carry farm efficiency using match 8461956309 data
```

Claude will call the tools to get real data and generate code that processes it.
