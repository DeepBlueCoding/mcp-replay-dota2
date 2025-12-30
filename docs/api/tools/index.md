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

    - **`get_hero_performance`**: THE tool for hero/ability questions. Returns kills, deaths, ability stats, per-fight breakdown. Use `ability_filter` for specific abilities, `start_time`/`end_time` for phase-specific analysis. **Call ONCE, don't chain.**
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

## Filtering

Many tools support **filtering** to narrow down results. Filters use **partial matching** (case-insensitive substring match) for hero names, locations, and abilities.

### Supported Filters

| Tool | Filters |
|------|---------|
| `get_hero_performance` | `ability_filter`, `start_time`, `end_time` |
| `get_hero_deaths` | `killer`, `victim`, `location`, `ability`, `start_time`, `end_time` |
| `list_fights` | `location`, `min_deaths`, `is_teamfight`, `start_time`, `end_time` |
| `get_teamfights` | `location`, `min_deaths`, `start_time`, `end_time` |

### Partial Matching

All string filters use **partial matching**:

```python
# These all match "juggernaut"
killer="jugg"
killer="jugger"
killer="naut"

# These all match "dire_t1_top"
location="t1"
location="dire"
location="top"

# These all match "faceless_void_chronosphere"
ability="chrono"
ability="void"
ability="sphere"
```

### Filter Examples

**Early game hero performance (0-15 min):**
```python
get_hero_performance(match_id=123, hero="spirit_breaker", start_time=0, end_time=900)
```

**Deaths by a specific hero:**
```python
get_hero_deaths(match_id=123, killer="medusa")
```

**Deaths at Roshan pit:**
```python
get_hero_deaths(match_id=123, location="roshan")
```

**Deaths by Chronosphere after 20 minutes:**
```python
get_hero_deaths(match_id=123, ability="chrono", start_time=1200)
```

**Teamfights at high ground (T3 towers):**
```python
list_fights(match_id=123, location="t3", is_teamfight=True)
```

**Late game teamfights (30+ minutes) with 4+ deaths:**
```python
get_teamfights(match_id=123, start_time=1800, min_deaths=4)
```

**Roshan pit fights:**
```python
list_fights(match_id=123, location="roshan")
```

### Available Locations (37 regions)

Filters can match any of these location names:

- **Towers**: `radiant_t1_top`, `radiant_t1_mid`, `radiant_t1_bot`, `radiant_t2_*`, `radiant_t3_*`, `radiant_t4`, `dire_t1_*`, `dire_t2_*`, `dire_t3_*`, `dire_t4`
- **Landmarks**: `roshan_pit`, `tormentor_radiant`, `tormentor_dire`
- **Farming areas**: `radiant_triangle`, `dire_triangle`, `radiant_ancients`, `dire_ancients`
- **Lanes/Areas**: `river`, `mid_lane`, `radiant_safelane`, `dire_safelane`, `radiant_jungle`, `dire_jungle`

Use partial matching for convenience:

| Filter | Matches |
|--------|---------|
| `"t1"` | All T1 tower areas (6 locations) |
| `"t3"` | All T3 tower areas / high ground (6 locations) |
| `"dire"` | All Dire-side locations |
| `"roshan"` | Roshan pit |
| `"jungle"` | Both jungle areas |
| `"triangle"` | Both triangle farming areas |
