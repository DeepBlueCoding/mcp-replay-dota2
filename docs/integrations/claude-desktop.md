# Claude Desktop

??? info "AI Summary"

    Add to `claude_desktop_config.json`: `{"mcpServers": {"dota2-match-analysis": {"command": "uvx", "args": ["dota2-match-analysis@latest"]}}}`. Restart Claude Desktop. Look for hammer icon (🔨) to verify. Ask naturally: "Analyze match 8461956309".

The simplest way to use this MCP server - just configure and chat.

## Setup

Add to your Claude Desktop config file:

**Linux:** `~/.config/claude/claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

!!! tip "Why @latest and --pull=always?"
    - `@latest` ensures uvx always downloads the newest version from PyPI
    - `--pull=always` ensures Docker always pulls the newest image
    - Both flags guarantee you're always running the most recent release

## Restart Claude Desktop

After saving the config, restart Claude Desktop completely (quit and reopen).

## Verify Connection

You should see a hammer icon (🔨) in the chat input area. Click it to see available tools:

- `get_hero_deaths`
- `get_combat_log`
- `get_fight_combat_log`
- `get_item_purchases`
- `get_objective_kills`
- `get_match_timeline`
- `get_stats_at_minute`
- `get_courier_kills`

## Usage

Just ask naturally:

> "Analyze match 8461956309. Why did Radiant lose the fight at 25 minutes?"

Claude will automatically:
1. Call `get_hero_deaths` to find deaths around that time
2. Call `get_fight_combat_log` to get fight details
3. Synthesize an analysis

## Troubleshooting

**No hammer icon?**

- Check the config file path is correct
- Ensure `uvx` is in your PATH (or `docker` for Docker method)
- Check Claude Desktop logs for errors

**Tools not working?**

- Test manually:

```bash
# Test uvx
uvx dota2-match-analysis@latest

# Test Docker
docker run --pull=always -i --rm dbcjuanma/mcp_replay_dota2
```
