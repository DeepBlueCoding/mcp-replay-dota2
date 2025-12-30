# Match Analysis Tools

These tools query match events, deaths, items, and timeline data. All require `match_id` as a parameter.

## download_replay

Pre-download and cache a replay file. **Use this first** before asking analysis questions about a new match. Replay files are large (50-400MB) and can take 1-5 minutes to download.

```python
download_replay(match_id=8461956309)
```

**Returns:**
```json
{
  "success": true,
  "match_id": 8461956309,
  "replay_path": "/home/user/dota2/replays/8461956309.dem",
  "file_size_mb": 398.0,
  "already_cached": false
}
```

If already cached:
```json
{
  "success": true,
  "match_id": 8461956309,
  "replay_path": "/home/user/dota2/replays/8461956309.dem",
  "file_size_mb": 398.0,
  "already_cached": true
}
```

!!! note "Automatic Retry"
    If a replay is corrupted during download or parsing, the server automatically deletes the corrupt file and retries once. If it still fails, use `delete_replay` to manually clear the cache before trying again.

!!! info "OpenDota Parse Wait"
    If the match hasn't been parsed by OpenDota yet (no `replay_url`), the server will:

    1. Request OpenDota to parse the match
    2. Poll for status every 30 seconds with progress updates showing elapsed time and attempt count
    3. Wait up to 1 hour for the parse to complete
    4. If timeout occurs, return an error suggesting to retry later

    For matches with existing `replay_url`, download proceeds immediately without waiting.

---

## delete_replay

Delete cached replay file and parsed data for a match. Use this when:

- A replay appears to be corrupted and needs to be re-downloaded
- You want to force a fresh download of a replay
- Cached parsed data seems incorrect or outdated

After deletion, the next analysis request for this match will trigger a fresh download and parse.

```python
delete_replay(match_id=8461956309)
```

**Returns:**
```json
{
  "success": true,
  "match_id": 8461956309,
  "file_deleted": true,
  "cache_deleted": true,
  "message": "Deleted replay file and parsed cache for match 8461956309"
}
```

If no cached data exists:
```json
{
  "success": true,
  "match_id": 8461956309,
  "file_deleted": false,
  "cache_deleted": false,
  "message": "No cached data found for match 8461956309"
}
```

---

## get_hero_deaths

Chronological list of ALL hero deaths in the match. Supports filtering by killer, victim, location, ability, and time range.

!!! warning "When NOT to use"
    - You already called `get_hero_performance` → It includes deaths per hero
    - Asking about specific hero's deaths → Use `get_hero_performance` instead
    - Asking about ability effectiveness → Use `get_hero_performance` instead

**Use for:**

- "Show me all deaths in the game" (global death timeline)
- "Who died the most?" (need to count across all heroes)
- "What was first blood?" (earliest death)
- Death pattern analysis across entire match
- "Deaths at Roshan pit" / "Deaths near T1 towers" (location-based)
- "Deaths by Lasso" / "Chronosphere kills" (ability-based)

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `match_id` | int | The Dota 2 match ID |
| `killer` | str (optional) | Filter by killer hero. Partial match: `"jugg"`, `"void"` |
| `victim` | str (optional) | Filter by victim hero. Partial match: `"es"`, `"medusa"` |
| `location` | str (optional) | Filter by death location. Partial match: `"t1"`, `"roshan"`, `"radiant"` |
| `ability` | str (optional) | Filter by killing ability. Partial match: `"lasso"`, `"chrono"` |
| `start_time` | float (optional) | Filter deaths after this game time (seconds) |
| `end_time` | float (optional) | Filter deaths before this game time (seconds) |

```python
# All deaths
get_hero_deaths(match_id=8461956309)

# Deaths by a specific hero
get_hero_deaths(match_id=8461956309, killer="medusa")

# Deaths at Roshan pit
get_hero_deaths(match_id=8461956309, location="roshan")

# Deaths by Chronosphere after 20 minutes
get_hero_deaths(match_id=8461956309, ability="chrono", start_time=1200)

# Deaths of a specific hero in early game
get_hero_deaths(match_id=8461956309, victim="earthshaker", end_time=600)
```

**Returns:**
```json
{
  "total_deaths": 45,
  "deaths": [
    {
      "game_time": 288,
      "game_time_str": "4:48",
      "victim": "earthshaker",
      "killer": "disruptor",
      "killer_is_hero": true,
      "ability": "disruptor_thunder_strike",
      "location": "dire_t1_top",
      "position": {"x": 4200, "y": 1800},
      "killer_level": 5,
      "victim_level": 4,
      "level_advantage": 1
    }
  ],
  "coaching_analysis": "AI analysis of death patterns (if client supports sampling)"
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `location` | Map region where death occurred (tower-based classification, e.g., `"dire_t1_top"`, `"roshan_pit"`, `"radiant_jungle"`) |
| `killer_level` | Killer's level at time of death (null if non-hero killer) |
| `victim_level` | Victim's level at time of death |
| `level_advantage` | `killer_level - victim_level` (positive = killer was higher level) |

**Available Locations (37 regions):**

- **Towers**: `radiant_t1_top`, `radiant_t1_mid`, `radiant_t1_bot`, `radiant_t2_*`, `radiant_t3_*`, `radiant_t4`, `dire_t1_*`, etc.
- **Landmarks**: `roshan_pit`, `tormentor_radiant`, `tormentor_dire`
- **Farming areas**: `radiant_triangle`, `dire_triangle`, `radiant_ancients`, `dire_ancients`
- **Lanes/Areas**: `river`, `mid_lane`, `radiant_safelane`, `dire_safelane`, `radiant_jungle`, etc.

!!! tip "Level Advantage Analysis"
    Use `level_advantage` to identify:

    - **Positive values**: Expected kills (higher level hero winning)
    - **Negative values**: Outplays or ganks (lower level hero getting the kill)
    - **Large negative values (-3 or more)**: Significant outplays or team rotations

---

## get_hero_performance

**THE PRIMARY TOOL for hero/ability analysis.** Use this FIRST and ONLY for any question about how a player/hero/ability performed.

**Use for:**

- "How did X hero perform?" / "How many kills did X get?"
- "How many Chronospheres landed?" / "Analyze Lasso effectiveness"
- "Show me fight participation" / "What was X's impact?"
- "How did X perform in early game?" (use `start_time`/`end_time`)

**Response includes (no need for additional tools):**

- `total_kills`, `total_deaths`, `total_assists` (aggregated)
- `ability_summary`: casts, hero_hits, hit_rate per ability
- `fights[]`: per-fight breakdown with kills/deaths/abilities used
- `avg_kill_level_advantage`: average level advantage when getting kills
- `avg_death_level_disadvantage`: average level disadvantage when dying
- `coaching_analysis`: AI evaluation (if client supports sampling)

!!! danger "DO NOT chain to other tools after this"
    - ❌ Don't call `get_fight_combat_log` - `fights[]` already has per-fight data
    - ❌ Don't call `get_hero_deaths` - `total_deaths` already included
    - ❌ Don't call `list_fights` - `fights[]` already lists all fights

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `match_id` | int | The Dota 2 match ID |
| `hero` | str | Hero name (e.g., "jakiro", "mars", "batrider") |
| `ability_filter` | str (optional) | Filter to specific ability (e.g., "ice_path", "flaming_lasso") |
| `start_time` | float (optional) | Filter fights starting after this game time (seconds) |
| `end_time` | float (optional) | Filter fights starting before this game time (seconds) |

**For ability questions:** Use `ability_filter` param (e.g., "flaming_lasso", "chronosphere").
The response shows: casts, hits on heroes, and kills in fights where ability was used.

**For phase-specific analysis:** Use `start_time`/`end_time` to filter to early game (0-900s), mid game (900-1800s), etc.

```python
# Full match analysis
get_hero_performance(
    match_id=8461956309,
    hero="earthshaker"
)

# Early game only (0-15 min)
get_hero_performance(
    match_id=8461956309,
    hero="spirit_breaker",
    start_time=0,
    end_time=900
)
```

**Returns:**
```json
{
  "success": true,
  "match_id": 8461956309,
  "hero": "earthshaker",
  "total_fights": 3,
  "total_teamfights": 1,
  "total_kills": 2,
  "total_deaths": 2,
  "total_assists": 0,
  "avg_kill_level_advantage": 1.5,
  "avg_death_level_disadvantage": -0.5,
  "ability_summary": [
    {"ability": "earthshaker_fissure", "total_casts": 3, "hero_hits": 6, "hit_rate": 200.0},
    {"ability": "earthshaker_enchant_totem", "total_casts": 3, "hero_hits": 2, "hit_rate": 66.7},
    {"ability": "earthshaker_echo_slam", "total_casts": 1, "hero_hits": 0, "hit_rate": 0.0}
  ],
  "fights": [
    {
      "fight_id": "fight_1",
      "fight_start": 288.0,
      "fight_start_str": "4:48",
      "fight_end": 295.0,
      "fight_end_str": "4:55",
      "is_teamfight": false,
      "hero_level": 6,
      "kills": 0,
      "deaths": 1,
      "assists": 0,
      "damage_dealt": 53,
      "damage_received": 366,
      "abilities_used": [
        {"ability": "earthshaker_enchant_totem", "total_casts": 1, "hero_hits": 0, "hit_rate": 0.0}
      ]
    }
  ]
}
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `ability_summary` | Overall ability usage across all fights |
| `hero_hits` | Times ability affected an enemy hero (includes stuns/debuffs from ground-targeted abilities like Ice Path, Fissure) |
| `hit_rate` | Can exceed 100% for AoE abilities that hit multiple heroes per cast |
| `fights` | Per-fight breakdown with K/D/A and ability usage |
| `is_teamfight` | True if the fight had 3+ deaths |
| `avg_kill_level_advantage` | Average level advantage when getting kills (positive = usually ahead) |
| `avg_death_level_disadvantage` | Average level disadvantage when dying (negative = dying to higher level) |
| `hero_level` | Hero's level at the start of each fight (in `fights[]`) |

!!! tip "Ground-Targeted Abilities"
    Abilities like Ice Path, Fissure, and Kinetic Field are tracked via MODIFIER_ADD events (stun debuffs applied to heroes), not just the cast event. This ensures accurate hit detection for ground-targeted CC abilities.

---

## get_raw_combat_events

Raw combat events for a **SPECIFIC TIME WINDOW** (advanced use).

!!! warning "When NOT to use"
    - Hero/ability performance → Use `get_hero_performance` instead
    - Fight summaries → Use `list_fights` or `get_teamfights` instead

**Use when:**

- Need raw events in a specific time range (not fight-based)
- Analyzing non-fight moments (e.g., "What happened at Roshan at 18:00?")

```python
# Default: narrative detail (recommended for most queries)
get_raw_combat_events(
    match_id=8461956309,
    start_time=280,
    end_time=300,
    hero_filter="earthshaker"
)

# Tactical: includes hero-to-hero damage
get_raw_combat_events(
    match_id=8461956309,
    start_time=280,
    end_time=300,
    detail_level="tactical"
)

# Full: all events (WARNING: can overflow context)
get_raw_combat_events(
    match_id=8461956309,
    start_time=280,
    end_time=290,  # Keep time range SHORT!
    detail_level="full"
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `match_id` | int | Required. The match ID |
| `start_time` | float | Optional. Filter events after this game time (seconds). **Note:** Pre-game purchases happen at negative times (~-80s). Use `-90` to include strategy phase, or omit entirely. `start_time=0` excludes pre-game. |
| `end_time` | float | Optional. Filter events before this game time (seconds) |
| `hero_filter` | string | Optional. Only events involving this hero (e.g., "earthshaker") |
| `detail_level` | string | Controls verbosity: `"narrative"` (default), `"tactical"`, or `"full"`. See below. |
| `max_events` | int | Maximum events to return (default 500, max 2000). Prevents overflow. |

**Detail Levels:**

| Level | ~Tokens | Best For |
|-------|---------|----------|
| `narrative` | 500-2,000 | "What happened?" - Deaths, abilities, items, purchases, buybacks |
| `tactical` | 2,000-5,000 | "How much damage?" - Adds hero-to-hero damage, debuffs on heroes |
| `full` | 50,000+ | Debugging only - All events including creeps. **⚠️ WARNING: Can overflow context** |

**Narrative Mode (default):**

| Included | Event Type | Description |
|----------|------------|-------------|
| ✅ | `ABILITY` | Hero ability casts |
| ✅ | `DEATH` | Hero deaths only |
| ✅ | `ITEM` | Active item usage |
| ✅ | `PURCHASE` | Item purchases |
| ✅ | `BUYBACK` | Buybacks |

**Tactical Mode (adds):**

| Added | Event Type | Description |
|-------|------------|-------------|
| ➕ | `DAMAGE` | Hero-to-hero damage only |
| ➕ | `MODIFIER_ADD` | Debuffs applied to heroes |

**Full Mode:**

| Added | Event Type | Reason to avoid |
|-------|------------|-----------------|
| ➕ | All `DAMAGE` | Creep/tower damage creates noise |
| ➕ | All `MODIFIER_*` | Buff/debuff spam |
| ➕ | `HEAL` | Minor heals flood log |

**When to use each level:**

- **`narrative`** (default): Fight overview, rotation analysis, item timings
- **`tactical`**: Damage breakdown, ability impact analysis
- **`full`**: Debugging only, with **short time windows (<30s)**

**Returns:**
```json
{
  "events": [
    {
      "type": "DAMAGE",
      "game_time": 285,
      "game_time_str": "4:45",
      "attacker": "disruptor",
      "attacker_is_hero": true,
      "target": "earthshaker",
      "target_is_hero": true,
      "ability": "disruptor_thunder_strike",
      "value": 160
    }
  ]
}
```

Event types: `DAMAGE`, `MODIFIER_ADD`, `MODIFIER_REMOVE`, `ABILITY`, `ITEM`, `DEATH`, `HEAL`, `PURCHASE`, `BUYBACK`

---

## get_fight_combat_log

Get detailed event-by-event combat log for **ONE SPECIFIC FIGHT**.

**Use when user asks for deep fight analysis:**

- "What exactly happened in the fight at 25:30?"
- "Break down the teamfight where we lost"
- "Show me the sequence of events in that fight"

!!! warning "When NOT to use"
    - You already called `get_hero_performance` → It has fight summaries
    - Asking about hero/ability stats → Use `get_hero_performance` instead
    - Want to see all fights → Use `list_fights` or `get_teamfights`

Auto-detects fight boundaries around a reference time. Returns combat events plus **fight highlights** including multi-hero abilities, kill streaks, and team wipes.

```python
# Default: narrative detail (recommended)
get_fight_combat_log(
    match_id=8461956309,
    reference_time=288,    # e.g., death time from get_hero_deaths
    hero="earthshaker"     # optional: anchor detection to this hero
)

# Tactical: for damage analysis
get_fight_combat_log(
    match_id=8461956309,
    reference_time=288,
    detail_level="tactical"
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `match_id` | int | Required. The match ID |
| `reference_time` | float | Required. Game time in seconds to anchor fight detection (e.g., death time) |
| `hero` | string | Optional. Hero name to anchor fight detection |
| `detail_level` | string | `"narrative"` (default), `"tactical"`, or `"full"`. Same as `get_combat_log`. |
| `max_events` | int | Maximum events (default 200). Prevents overflow. |

**Returns:**
```json
{
  "fight_start": 280,
  "fight_end": 295,
  "fight_start_str": "4:40",
  "fight_end_str": "4:55",
  "duration": 15,
  "participants": ["earthshaker", "disruptor", "naga_siren", "medusa"],
  "total_events": 47,
  "events": [...],
  "highlights": {
    "multi_hero_abilities": [
      {
        "game_time": 282.5,
        "game_time_str": "4:42",
        "ability": "faceless_void_chronosphere",
        "ability_display": "Chronosphere",
        "caster": "faceless_void",
        "targets": ["crystal_maiden", "lion", "earthshaker"],
        "hero_count": 3
      }
    ],
    "kill_streaks": [
      {
        "game_time": 290.0,
        "game_time_str": "4:50",
        "hero": "medusa",
        "streak_type": "triple_kill",
        "kills": 3,
        "victims": ["crystal_maiden", "lion", "earthshaker"]
      }
    ],
    "team_wipes": [
      {
        "game_time": 295.0,
        "game_time_str": "4:55",
        "team_wiped": "radiant",
        "killer_team": "dire",
        "duration": 13.0
      }
    ],
    "bkb_blink_combos": [
      {
        "game_time": 282.0,
        "game_time_str": "4:42",
        "hero": "earthshaker",
        "ability": "earthshaker_echo_slam",
        "ability_display": "Echo Slam",
        "bkb_time": 281.5,
        "blink_time": 281.8,
        "is_initiator": true
      }
    ],
    "coordinated_ults": [
      {
        "game_time": 282.0,
        "game_time_str": "4:42",
        "team": "radiant",
        "heroes": ["earthshaker", "nevermore"],
        "abilities": ["earthshaker_echo_slam", "nevermore_requiem"],
        "window_seconds": 1.5
      }
    ],
    "clutch_saves": [
      {
        "game_time": 290.0,
        "game_time_str": "4:50",
        "saved_hero": "medusa",
        "save_type": "self_banish",
        "save_ability": "item_outworld_staff",
        "saved_from": "juggernaut_omni_slash",
        "saver": null
      }
    ],
    "refresher_combos": [],
    "buybacks": [],
    "generic_aoe_hits": []
  }
}
```

**Highlights Explained:**

| Field | Description |
|-------|-------------|
| `multi_hero_abilities` | Big ultimates/abilities hitting 2+ enemy heroes (Chronosphere, Black Hole, Ravage, Ice Path, etc.) |
| `kill_streaks` | Double kill through Rampage (uses Dota 2's 18-second window between kills) |
| `team_wipes` | All 5 heroes of one team killed within the fight (Ace!) |
| `bkb_blink_combos` | BKB + Blink into big ability (classic initiation pattern). `is_initiator=true` for first combo, `false` for follow-ups |
| `coordinated_ults` | 2+ heroes from the **same team** using big abilities within 3 seconds. Includes `team` field (radiant/dire) |
| `clutch_saves` | Self-saves (Outworld Staff, Euls) or ally saves (Glimmer Cape on teammates under attack) |
| `refresher_combos` | Hero using Refresher to double-cast an ultimate (double Echo Slam, double Ravage, etc.) |
| `buybacks` | Heroes buying back during the fight |
| `generic_aoe_hits` | Any ability hitting 3+ heroes (catches abilities not in the big-ability list) |

**Tracked Abilities (60+):**
- **Ultimates**: Chronosphere, Black Hole, Ravage, Reverse Polarity, Echo Slam, Requiem of Souls, etc.
- **Control**: Ice Path, Kinetic Field, Dream Coil, Static Storm, etc.
- **Team wipe detectors**: Tracks all deaths to determine if entire team was killed
- **Initiation**: BKB + Blink combos with is_initiator flag for the first combo

---

## get_item_purchases

When items were bought.

```python
get_item_purchases(
    match_id=8461956309,
    hero_filter="antimage"  # optional
)
```

**Returns:**
```json
{
  "purchases": [
    {"game_time": -89, "game_time_str": "-1:29", "hero": "antimage", "item": "item_tango"},
    {"game_time": 540, "game_time_str": "9:00", "hero": "antimage", "item": "item_bfury"}
  ]
}
```

Negative times = purchased before horn (0:00).

---

## get_objective_kills

Roshan, tormentor, towers, barracks.

```python
get_objective_kills(match_id=8461956309)
```

**Returns:**
```json
{
  "roshan_kills": [
    {"game_time": 1392, "game_time_str": "23:12", "killer": "medusa", "team": "dire", "kill_number": 1}
  ],
  "tormentor_kills": [
    {"game_time": 1215, "game_time_str": "20:15", "killer": "medusa", "team": "dire", "side": "dire"}
  ],
  "tower_kills": [
    {"game_time": 669, "game_time_str": "11:09", "tower": "dire_t1_mid", "team": "dire", "tier": 1, "lane": "mid", "killer": "nevermore"}
  ],
  "barracks_kills": [
    {"game_time": 2373, "game_time_str": "39:33", "barracks": "radiant_melee_mid", "team": "radiant", "lane": "mid", "type": "melee", "killer": "medusa"}
  ]
}
```

---

## get_match_timeline

Net worth, XP, KDA over time for all players.

```python
get_match_timeline(match_id=8461956309)
```

**Returns:**
```json
{
  "players": [
    {
      "hero": "antimage",
      "team": "dire",
      "net_worth": [500, 800, 1200, ...],  // every 30 seconds
      "hero_damage": [0, 0, 150, ...],
      "kda_timeline": [
        {"game_time": 0, "kills": 0, "deaths": 0, "assists": 0, "level": 1},
        {"game_time": 300, "kills": 0, "deaths": 0, "assists": 0, "level": 5}
      ]
    }
  ],
  "team_graphs": {
    "radiant_xp": [0, 1200, 2500, ...],
    "dire_xp": [0, 1100, 2400, ...],
    "radiant_gold": [0, 600, 1300, ...],
    "dire_gold": [0, 650, 1400, ...]
  }
}
```

---

## get_stats_at_minute

Snapshot of all players at a specific minute. **Parallel-safe**: call for multiple minutes.

```python
get_stats_at_minute(match_id=8461956309, minute=10)
```

**Returns:**
```json
{
  "minute": 10,
  "players": [
    {
      "hero": "antimage",
      "team": "dire",
      "net_worth": 5420,
      "last_hits": 78,
      "denies": 8,
      "kills": 0,
      "deaths": 0,
      "assists": 0,
      "level": 10,
      "hero_damage": 450
    }
  ]
}
```

---

## get_courier_kills

Courier snipes.

```python
get_courier_kills(match_id=8461956309)
```

**Returns:**
```json
{
  "kills": [
    {
      "game_time": 420,
      "game_time_str": "7:00",
      "killer": "bounty_hunter",
      "killer_is_hero": true,
      "owner": "antimage",
      "team": "dire",
      "position": {"x": 2100, "y": -1500, "region": "river", "location": "River near Radiant outpost"}
    }
  ]
}
```

---

## get_rune_pickups

All rune pickups in the match.

```python
get_rune_pickups(match_id=8461956309)
```

**Returns:**
```json
{
  "pickups": [
    {
      "game_time": 0,
      "game_time_str": "0:00",
      "hero": "pangolier",
      "rune_type": "bounty"
    }
  ],
  "total_pickups": 42
}
```

---

## get_match_draft

Complete draft with bans and picks in order (for Captains Mode matches). Includes **position assignment** (1-5), **lane assignment** (safelane/mid/offlane), and **draft timing data** for each hero.

```python
get_match_draft(match_id=8461956309)
```

**Returns:**
```json
{
  "match_id": 8461956309,
  "game_mode": 2,
  "game_mode_name": "Captains Mode",
  "radiant_picks": [
    {
      "order": 10,
      "is_pick": true,
      "team": "radiant",
      "hero_id": 8,
      "hero_name": "juggernaut",
      "localized_name": "Juggernaut",
      "position": 1,
      "lane": "safelane"
    },
    {
      "order": 8,
      "is_pick": true,
      "team": "radiant",
      "hero_id": 11,
      "hero_name": "nevermore",
      "localized_name": "Shadow Fiend",
      "position": 2,
      "lane": "mid"
    }
  ],
  "radiant_bans": [
    {
      "order": 1,
      "is_pick": false,
      "team": "radiant",
      "hero_id": 23,
      "hero_name": "kunkka",
      "localized_name": "Kunkka",
      "position": null,
      "lane": null
    }
  ],
  "dire_picks": [...],
  "dire_bans": [...],
  "draft_timings": [
    {
      "order": 1,
      "is_pick": false,
      "active_team": "radiant",
      "hero_id": 23,
      "player_slot": null,
      "extra_time": 130,
      "total_time_taken": 15
    }
  ]
}
```

**Position and Lane Fields:**

| Field | Description |
|-------|-------------|
| `position` | Player role (1-5) for picks, `null` for bans |
| `lane` | Expected lane based on position, `null` for bans |

**Position to Lane Mapping:**

| Position | Role | Lane |
|----------|------|------|
| 1 | Carry | `safelane` |
| 2 | Mid | `mid` |
| 3 | Offlane | `offlane` |
| 4 | Soft support | `offlane` (with pos 3) |
| 5 | Hard support | `safelane` (with pos 1) |

**Draft Timings Fields (OpenDota SDK 7.40.1+):**

| Field | Description |
|-------|-------------|
| `order` | Draft order (1-24 for CM) |
| `is_pick` | True if pick, False if ban |
| `active_team` | Team making this selection ("radiant" or "dire") |
| `hero_id` | Hero ID selected |
| `player_slot` | Player slot if this is a pick (null for bans) |
| `extra_time` | Extra time remaining after this selection (seconds) |
| `total_time_taken` | Time spent on this selection (seconds) |

!!! tip "Lane Matchup Analysis"
    Use the `lane` field to construct lane matchups. For Radiant: safelane = bottom lane, offlane = top lane. For Dire: safelane = top lane, offlane = bottom lane.

    Example matchups from position data:

    - **Radiant Safelane (bot)**: Pos 1 + Pos 5 vs enemy Pos 3 + Pos 4
    - **Mid**: Pos 2 vs enemy Pos 2
    - **Radiant Offlane (top)**: Pos 3 + Pos 4 vs enemy Pos 1 + Pos 5

!!! note "Counter Picks Data"
    For hero counter picks and matchup analysis, use the `dota2://heroes/all` resource which contains `counters`, `good_against`, and `when_to_pick` for all 126 heroes.

---

## get_match_info

Match metadata including teams, players, winner, duration, and match analysis fields.

```python
get_match_info(match_id=8461956309)
```

**Returns:**
```json
{
  "match_id": 8461956309,
  "is_pro_match": true,
  "league_id": 18324,
  "league": {
    "league_id": 18324,
    "name": "The International 2024",
    "tier": "premium"
  },
  "game_mode": 2,
  "game_mode_name": "Captains Mode",
  "winner": "dire",
  "duration_seconds": 4672,
  "duration_str": "77:52",
  "pre_game_duration": 90,
  "comeback": 0.15,
  "stomp": 0.02,
  "radiant_team": {"team_id": 8291895, "team_tag": "XG", "team_name": "XG", "logo_url": "https://..."},
  "dire_team": {"team_id": 8894818, "team_tag": "FLCN", "team_name": "FLCN", "logo_url": "https://..."},
  "players": [
    {"player_name": "Ame", "hero_name": "juggernaut", "hero_localized": "Juggernaut", "team": "radiant", "steam_id": 123456}
  ],
  "radiant_players": [...],
  "dire_players": [...]
}
```

**New Fields (OpenDota SDK 7.40.1+):**

| Field | Description |
|-------|-------------|
| `league` | League info object with `league_id`, `name`, and `tier` |
| `pre_game_duration` | Duration before horn in seconds (strategy phase) |
| `comeback` | Comeback factor (0.0-1.0, higher = bigger comeback by winner) |
| `stomp` | Stomp factor (0.0-1.0, higher = more one-sided match) |
| `logo_url` | Team logo URL from OpenDota (in team objects) |

!!! tip "Match Analysis"
    Use `comeback` and `stomp` to quickly identify close games vs one-sided matches:

    - **High stomp (>0.5)**: Dominant victory, likely draft/lane advantage
    - **High comeback (>0.5)**: Team recovered from losing position
    - **Low both (<0.2)**: Evenly contested match

---

## get_match_heroes

Get the 10 heroes in a match with detailed stats, **position assignment**, **counter picks data**, and **player performance metrics** for analysis.

```python
get_match_heroes(match_id=8461956309)
```

**Returns:**
```json
{
  "radiant_heroes": [
    {
      "hero_id": 1,
      "hero_name": "antimage",
      "localized_name": "Anti-Mage",
      "team": "radiant",
      "position": 1,
      "lane": "safe_lane",
      "role": "core",
      "kills": 8,
      "deaths": 2,
      "assists": 5,
      "last_hits": 420,
      "gpm": 650,
      "xpm": 580,
      "net_worth": 28500,
      "hero_damage": 15200,
      "items": ["Manta Style", "Battle Fury", "Abyssal Blade"],
      "player_name": "PlayerOne",
      "pro_name": "Yatoro",
      "rank_tier": 80,
      "teamfight_participation": 0.65,
      "stuns": 12.5,
      "camps_stacked": 3,
      "obs_placed": 0,
      "sen_placed": 2,
      "lane_efficiency": 0.85,
      "item_neutral2": "item_havoc_hammer",
      "counters": [
        {"hero_id": 6, "localized_name": "Doom", "reason": "Doom silences AM completely..."}
      ],
      "good_against": [
        {"hero_id": 94, "localized_name": "Medusa", "reason": "Mana Break devastates mana shield..."}
      ],
      "when_to_pick": ["Enemy has mana-dependent heroes", "Team can hold 4v5"]
    }
  ],
  "dire_heroes": [...]
}
```

**Position Field:**

| Position | Role | Lane |
|----------|------|------|
| 1 | Carry | Safelane core |
| 2 | Mid | Mid lane |
| 3 | Offlane | Offlane core |
| 4 | Soft support | Higher GPM support |
| 5 | Hard support | Lowest GPM support |

**New Fields (OpenDota SDK 7.40.1+):**

| Field | Description |
|-------|-------------|
| `rank_tier` | Player rank tier (e.g., 80+ = Immortal, 85 = Divine 5) |
| `teamfight_participation` | Percentage of team kills player was involved in (0.0-1.0) |
| `stuns` | Total stun duration dealt to enemies in seconds |
| `camps_stacked` | Number of neutral camps stacked |
| `obs_placed` | Observer wards placed |
| `sen_placed` | Sentry wards placed |
| `lane_efficiency` | Lane efficiency score (0.0-1.0, gold earned vs max possible) |
| `item_neutral2` | Second neutral item slot (patch 7.40+) |

!!! tip "Draft Analysis"
    Use the `counters` and `good_against` fields to analyze draft advantages. The `position` field tells you which role each hero played (1-5).

!!! tip "Support Analysis"
    Use `obs_placed`, `sen_placed`, and `camps_stacked` to evaluate support performance. High `teamfight_participation` on supports indicates good positioning.

---

## get_match_players

Get the 10 players in a match with their hero assignments, **position (1-5)**, and **rank tier**.

```python
get_match_players(match_id=8461956309)
```

**Returns:**
```json
{
  "radiant": [
    {
      "player_name": "PlayerOne",
      "pro_name": "Yatoro",
      "account_id": 311360822,
      "hero_id": 1,
      "hero_name": "antimage",
      "localized_name": "Anti-Mage",
      "position": 1,
      "rank_tier": 80
    }
  ],
  "dire": [...]
}
```

**Fields:**

| Field | Description |
|-------|-------------|
| `position` | Player's role (1=carry, 2=mid, 3=offlane, 4=soft support, 5=hard support) |
| `rank_tier` | Player rank tier (OpenDota SDK 7.40.1+). Can be null for pro matches. |

**Rank Tier Values:**

| Range | Rank |
|-------|------|
| 10-15 | Herald |
| 20-25 | Guardian |
| 30-35 | Crusader |
| 40-45 | Archon |
| 50-55 | Legend |
| 60-65 | Ancient |
| 70-75 | Divine |
| 80+ | Immortal |

---

# Diagnostic Tools

## get_client_capabilities

Check what MCP capabilities the connected client supports. Use this to verify if features like sampling are available.

```python
get_client_capabilities()
```

**Returns:**
```json
{
  "sampling_supported": true,
  "roots_supported": true,
  "client_info": {
    "name": "claude-code",
    "version": "1.0.50"
  },
  "raw_capabilities": "ClientCapabilities(sampling=SamplingCapability(), roots=...)"
}
```

**Key Fields:**

| Field | Description |
|-------|-------------|
| `sampling_supported` | `true` if client supports LLM sampling via `ctx.sample()` |
| `roots_supported` | `true` if client supports workspace roots |
| `client_info` | Client name and version from initialization |
| `raw_capabilities` | Raw capabilities object for debugging |

!!! tip "Sampling Support"
    If `sampling_supported` is `true`, the server can use `ctx.sample()` to request LLM completions from the client. This enables automatic coaching analysis in tool responses.

    If `false`, tools will return data without AI-generated coaching insights.
