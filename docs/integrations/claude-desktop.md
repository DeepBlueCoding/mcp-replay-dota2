# Claude Desktop

??? info "🤖 AI Summary"

    Add to `claude_desktop_config.json`: `{"mcpServers": {"dota2": {"command": "uv", "args": ["run", "--frozen", "--project", "/path/to/repo", "python", "/path/to/repo/dota_match_mcp_server.py"]}}}`. Restart Claude Desktop. Look for hammer icon (🔨) to verify. Ask naturally: "Analyze match 8461956309".

The simplest way to use this MCP server - just configure and chat.

## Setup

Add to your Claude Desktop config file:

**Linux:** `~/.config/claude/claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

=== "Linux/macOS"

    ```json
    {
      "mcpServers": {
        "dota2": {
          "command": "uv",
          "args": [
            "run",
            "--frozen",
            "--project", "/home/user/projects/mcp_replay_dota2",
            "python",
            "/home/user/projects/mcp_replay_dota2/dota_match_mcp_server.py"
          ]
        }
      }
    }
    ```

=== "Windows"

    ```json
    {
      "mcpServers": {
        "dota2": {
          "command": "uv",
          "args": [
            "run",
            "--frozen",
            "--project", "C:\\Users\\username\\projects\\mcp_replay_dota2",
            "python",
            "C:\\Users\\username\\projects\\mcp_replay_dota2\\dota_match_mcp_server.py"
          ]
        }
      }
    }
    ```

!!! tip "Why `--frozen --project`?"
    - `--frozen` ensures dependencies are locked (no unexpected updates)
    - `--project` explicitly sets the project path (avoids working directory issues)

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
- Ensure `uv` is in your PATH
- Check Claude Desktop logs for errors

**Tools not working?**

- Verify the `--project` path points to the cloned repository
- Test manually:

```bash
uv run --frozen --project /path/to/mcp_replay_dota2 python /path/to/mcp_replay_dota2/dota_match_mcp_server.py
```
