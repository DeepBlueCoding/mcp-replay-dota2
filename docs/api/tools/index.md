# Tools Reference

??? info "AI Summary - Tool Selection Guide"

    **CRITICAL: Choose the right tool FIRST to avoid redundant calls.**

    | Question Type | Use This Tool | DO NOT Chain To |
    |--------------|---------------|-----------------|
    | Hero/ability performance | `get_hero_performance` | ❌ `get_fight_combat_log`, `get_hero_deaths`, `list_fights` |
    | Deep fight breakdown | `get_fight_combat_log` | ❌ `get_hero_performance` (if already called) |
    | All deaths in match | `get_hero_deaths` | ❌ `get_hero_performance` (for same hero) |
    | Fight overview | `list_fights` or `get_teamfights` | ❌ `get_fight_combat_log` for each fight |
    | Farming patterns | `get_farming_pattern` | - |
    | Rotations | `get_rotation_analysis` | - |

    **Primary Tools:**

    - **`get_hero_performance`**: THE tool for hero/ability questions. Returns kills, deaths, ability stats, per-fight breakdown. Use `ability_filter` for specific abilities. **Call ONCE, don't chain.**
    - **`get_fight_combat_log`**: Deep event-by-event fight analysis. Use when user asks "what happened in the fight at X?"
    - **`get_farming_pattern`**: THE tool for farming questions. Returns minute-by-minute data. **Replaces 25+ tool calls.**
    - **`get_rotation_analysis`**: THE tool for rotation questions. Detects lane departures, correlates with runes.

    **Pro Scene Tools**: `search_pro_player`, `search_team`, `get_pro_player_by_name`, `get_team_by_name`, `get_pro_matches`, `get_league_matches`.

    **Parallel-safe tools**: `get_stats_at_minute`, `get_cs_at_minute`, `get_hero_positions`, `get_snapshot_at_time`, `get_fight`, `get_position_timeline`, `get_fight_replay`.

Tools are functions the LLM can call. All match analysis tools take `match_id` as required parameter.

## Tool Categories

| Category | Description | Tools |
|----------|-------------|-------|
| [Match Analysis](match-analysis.md) | Query match events, deaths, items, timeline | 15 tools |
| [Pro Scene](pro-scene.md) | Search players, teams, leagues, pro matches | 10 tools |
| [Game State](game-state.md) | High-resolution positions, snapshots, fights | 11 tools |
| [Farming & Rotation](farming-rotation.md) | Farming patterns and rotation analysis | 2 tools |

## Parallel Tool Execution

Many tools are **parallel-safe** and can be called simultaneously with different parameters. This significantly speeds up analysis when comparing multiple time points or fights.

### Parallel-Safe Tools

| Tool | Parallelize By |
|------|----------------|
| `get_stats_at_minute` | Different minutes (e.g., 10, 20, 30) |
| `get_cs_at_minute` | Different minutes (e.g., 5, 10, 15) |
| `get_hero_positions` | Different minutes |
| `get_snapshot_at_time` | Different game times |
| `get_fight` | Different fight_ids |
| `get_position_timeline` | Different time ranges or heroes |
| `get_fight_replay` | Different fights |

### Example: Laning Analysis

Instead of calling sequentially:
```python
# Slow - sequential calls
get_cs_at_minute(match_id=123, minute=5)
get_cs_at_minute(match_id=123, minute=10)
```

Call both in parallel:
```python
# Fast - parallel calls in same LLM response
get_cs_at_minute(match_id=123, minute=5)  # AND
get_cs_at_minute(match_id=123, minute=10)
```

The LLM can issue multiple tool calls in a single response, and the runtime executes them concurrently.
