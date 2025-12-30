# Lane Analysis Tools

Detailed laning phase analysis tools for tracking CS, harass, tower proximity, rotations, and wave manipulation.

## get_lane_summary

Get comprehensive laning phase summary with all tracked events.

This is THE tool for questions about "who won the lane", "laning phase summary", "how did the laning go", or general laning performance questions.

```python
get_lane_summary(match_id=8461956309)
```

**Returns:**
```json
{
  "success": true,
  "match_id": 8461956309,
  "top_winner": "dire",
  "mid_winner": "radiant",
  "bot_winner": "radiant",
  "radiant_laning_score": 285.5,
  "dire_laning_score": 312.0,
  "hero_stats": [
    {
      "hero": "antimage",
      "team": "radiant",
      "lane": "bot",
      "role": "core",
      "last_hits_5min": 28,
      "last_hits_10min": 65,
      "denies_5min": 3,
      "denies_10min": 8,
      "gold_5min": 2100,
      "gold_10min": 4800,
      "level_5min": 5,
      "level_10min": 10,
      "lane_efficiency": 0.85,
      "damage_dealt_to_heroes": 450,
      "damage_received_from_heroes": 620,
      "time_under_own_tower": 45.5,
      "time_under_enemy_tower": 12.3,
      "last_hit_events": [...],
      "harass_events": [...],
      "neutral_aggro_events": [...],
      "tower_pressure_events": [...],
      "neutral_attacks": 50,
      "pull_attempts": 12,
      "tower_damage_taken": 450,
      "tower_hits_received": 3
    }
  ],
  "rotations": [...],
  "wave_nukes": [...],
  "neutral_aggro": [...],
  "tower_pressure": [...]
}
```

**Key Fields:**

| Field | Description |
|-------|-------------|
| `top_winner`, `mid_winner`, `bot_winner` | Lane winner: "radiant", "dire", or "even" |
| `hero_stats` | Per-hero laning stats including CS, gold, harass |
| `lane_efficiency` | Lane efficiency score from OpenDota (0.0-1.0, gold earned vs max possible). *New in SDK 7.40.1* |
| `time_under_own_tower` / `time_under_enemy_tower` | Seconds spent under tower (lane equilibrium indicator) |
| `last_hit_events` | Detailed list of every last hit/deny |
| `harass_events` | List of hero-to-hero damage events |
| `rotations` | Smoke breaks, TPs, twin gate usage |
| `wave_nukes` | AoE ability usage on lane creeps |
| `neutral_aggro` | All hero attacks on neutral creeps (pulls, farming) |
| `tower_pressure` | All tower damage taken by heroes |
| `neutral_attacks` | Count of neutral creep attacks per hero |
| `pull_attempts` | Count of pull-like neutral aggro per hero |
| `tower_damage_taken` | Total tower damage received per hero |
| `tower_hits_received` | Number of tower hits per hero |

!!! tip "Lane Efficiency"
    The `lane_efficiency` field (0.0-1.0) from OpenDota measures gold earned vs theoretical maximum:

    - **>0.8**: Excellent laning, free-farming
    - **0.6-0.8**: Good laning, some pressure
    - **0.4-0.6**: Contested lane
    - **<0.4**: Struggled in lane, likely lost

---

## get_cs_at_minute

Snapshot of CS data for all heroes at a specific minute.

```python
get_cs_at_minute(match_id=8461956309, minute=10)
```

**Returns:**
```json
{
  "antimage": {"last_hits": 65, "denies": 8, "gold": 4800, "level": 10},
  "medusa": {"last_hits": 72, "denies": 5, "gold": 5200, "level": 11}
}
```

**Example Questions:**

- "How many last hits did the carry have at 5 minutes?"
- "Compare CS between the two mids at 10 minutes"
- "Who had the most denies at minute 5?"

---

## Lane Analysis Service Methods

The `LaneService` provides detailed lane analysis through these methods:

### get_lane_last_hits

Get all last hit and deny events during laning phase with positions.

```python
from src.services.lane.lane_service import LaneService

lane_svc = LaneService()
last_hits = lane_svc.get_lane_last_hits(parsed_data, hero_filter="antimage")
```

**Returns:**
```json
[
  {
    "game_time": 35.2,
    "game_time_str": "0:35",
    "hero": "antimage",
    "target": "npc_dota_creep_badguys_melee",
    "is_deny": false,
    "position_x": -5200.0,
    "position_y": -4100.0,
    "lane": "bot"
  }
]
```

**Use for:**

- "Where did the carry farm each wave?"
- "How many denies did the offlaner get?"
- "Show all last hits in the first 2 minutes"

---

### get_lane_waves

Get wave-by-wave CS breakdown for a specific lane.

```python
from src.services.lane.lane_service import LaneService

lane_svc = LaneService()
waves = lane_svc.get_lane_waves(
    parsed_data,
    lane="bot",
    team="dire",
    hero_filter="juggernaut"
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | ParsedReplayData | required | Parsed replay data |
| `lane` | str | `"bot"` | Lane to analyze: "top", "mid", "bot" |
| `team` | str | `"radiant"` | Team whose creeps to track: "radiant" or "dire" |
| `hero_filter` | str | None | Filter CS to specific hero |
| `end_time` | float | 600.0 | End of laning phase (seconds) |

**Returns:**
```json
[
  {
    "wave_number": 1,
    "spawn_time": 0.0,
    "spawn_time_str": "0:00",
    "first_death_time": 42.5,
    "last_death_time": 58.2,
    "lane": "bot",
    "team": "dire",
    "melee_deaths": 2,
    "ranged_deaths": 1,
    "total_deaths": 3,
    "last_hits": [
      {
        "game_time": 42.5,
        "game_time_str": "0:42",
        "hero": "juggernaut",
        "target": "npc_dota_creep_badguys_melee",
        "is_deny": false,
        "lane": "bot",
        "wave_number": 1
      }
    ]
  },
  {
    "wave_number": 2,
    "spawn_time": 30.0,
    "spawn_time_str": "0:30",
    "first_death_time": 73.1,
    "last_death_time": 88.0,
    "lane": "bot",
    "team": "dire",
    "melee_deaths": 3,
    "ranged_deaths": 1,
    "total_deaths": 4,
    "last_hits": [...]
  }
]
```

**Use for:**

- "How many CS did the carry get on wave 1?"
- "Show wave-by-wave farming efficiency"
- "Which waves did they miss CS on?"
- "Compare first 3 waves between two carries"

!!! note "Wave Timing"
    Waves spawn every 30 seconds (0:00, 0:30, 1:00, etc.) but don't die immediately:

    - **Wave 1** (spawns 0:00) → creeps typically die **0:35 - 1:05**
    - **Wave 2** (spawns 0:30) → creeps typically die **1:05 - 1:35**
    - **Wave N** (spawns (N-1)*30) → creeps die **spawn+35 to spawn+65**

    The service uses non-overlapping 30-second death windows to assign each CS to the correct wave.

!!! tip "Wave Analysis Patterns"
    Common wave analysis use cases:

    - **Perfect CS check**: Wave has 3 melee + 1 ranged = 4 total
    - **First wave priority**: Getting all CS on wave 1 sets the tempo
    - **Lane dominance**: Consistent 3-4 CS per wave indicates control
    - **Recovery detection**: Low CS early, improving later shows adaptation

---

### get_lane_waves_v2

Enhanced wave detection using `entity_deaths` + `attacks` correlation (requires python-manta 1.4.5.4+).

```python
from src.services.lane.lane_service import LaneService

lane_svc = LaneService()
waves = lane_svc.get_lane_waves_v2(
    parsed_data,
    lane="bot",
    team="dire",
    hero_filter="juggernaut"
)
```

**What's different from get_lane_waves:**

| Feature | get_lane_waves | get_lane_waves_v2 |
|---------|----------------|-------------------|
| Death detection | Combat log | entity_deaths collector |
| Last hit attribution | Combat log DEATH events | Attack correlation |
| All creep deaths | Hero last-hits only | ALL creep deaths tracked |
| Contested CS | Not detected | Can be correlated |

**Returns:** Same `CreepWave` structure as `get_lane_waves`.

**Falls back** to `get_lane_waves` if `entity_deaths` collector not available.

---

### get_contested_cs

Detect contested CS - creeps attacked by 2+ heroes before death.

Uses `entity_deaths` + `attacks` correlation to find creeps where multiple heroes competed for the last hit.

```python
contested = lane_svc.get_contested_cs(parsed_data, lane="bot", team="dire")
```

**Returns:**
```json
[
  {
    "game_time": 45.2,
    "game_time_str": "0:45",
    "entity_id": 1234,
    "creep_name": "npc_dota_creep_badguys_melee",
    "wave_number": 1,
    "hero_attackers": ["juggernaut", "axe"],
    "last_hitter": "juggernaut",
    "total_attacks": 8,
    "hero_attacks": 5
  }
]
```

**Use for:**

- "How many creeps were contested in lane?"
- "Who won the contested last hits?"
- "Show trades where both heroes went for the same creep"

!!! note "Requires python-manta 1.4.5.4+"
    This feature requires the `entity_deaths` and `attacks` collectors.
    Returns empty list if collectors not available.

---

### get_lane_harass

Get hero-to-hero damage events during laning phase.

```python
harass = lane_svc.get_lane_harass(parsed_data, hero_filter="lion")
```

**Returns:**
```json
[
  {
    "game_time": 42.5,
    "game_time_str": "0:42",
    "attacker": "lion",
    "target": "antimage",
    "damage": 65,
    "ability": "lion_impale",
    "lane": "bot"
  }
]
```

**Use for:**

- "How much harass did the support deal?"
- "Who took the most damage in lane?"
- "Show me trading patterns in top lane"

---

### get_tower_proximity_timeline

Track when heroes enter/leave tower range (detected via `modifier_tower_aura_bonus`).

```python
tower_events = lane_svc.get_tower_proximity_timeline(parsed_data, hero_filter="antimage")
```

**Returns:**
```json
[
  {
    "game_time": 45.0,
    "game_time_str": "0:45",
    "hero": "antimage",
    "tower_team": "radiant",
    "event_type": "entered"
  },
  {
    "game_time": 52.0,
    "game_time_str": "0:52",
    "hero": "antimage",
    "tower_team": "radiant",
    "event_type": "left"
  }
]
```

**Use for:**

- "How long was the carry under tower?"
- "When did the lane push into enemy tower?"
- "Track lane equilibrium via tower proximity"

!!! note "Tower Aura Detection"
    Tower proximity is detected via the `modifier_tower_aura_bonus` buff which applies to heroes within 700 units of their own tower. This detects when heroes are near their allied tower.

---

### get_wave_nukes

Detect when heroes use AoE abilities to damage multiple lane creeps.

```python
nukes = lane_svc.get_wave_nukes(parsed_data, hero_filter="pugna")
```

**Returns:**
```json
[
  {
    "game_time": 28.5,
    "game_time_str": "0:28",
    "hero": "pugna",
    "ability": "pugna_nether_blast",
    "creeps_hit": 4,
    "total_damage": 280,
    "lane": "top"
  }
]
```

**Use for:**

- "Did the support push the wave?"
- "When did they nuke the creep wave?"
- "Track intentional wave manipulation"

---

### get_lane_rotations

Detect rotation events: smoke breaks, TP scrolls, twin gate usage.

```python
rotations = lane_svc.get_lane_rotations(parsed_data, hero_filter="lion")
```

**Returns:**
```json
[
  {
    "game_time": 180.0,
    "game_time_str": "3:00",
    "hero": "lion",
    "rotation_type": "smoke_break",
    "from_position_x": -4500.0,
    "from_position_y": 800.0,
    "to_lane": "mid"
  },
  {
    "game_time": 320.0,
    "game_time_str": "5:20",
    "hero": "earthshaker",
    "rotation_type": "tp_scroll",
    "from_position_x": 2100.0,
    "from_position_y": -1500.0,
    "to_lane": null
  }
]
```

**Rotation Types:**

| Type | Description |
|------|-------------|
| `smoke_break` | Smoke revealed (hero entered enemy vision/proximity) |
| `tp_scroll` | Hero started teleporting |
| `twin_gate` | Hero used twin gate portal |

---

### get_neutral_aggro

Get all hero attacks on neutral creeps during laning phase (0-10 minutes).

```python
neutral_events = lane_svc.get_neutral_aggro(parsed_data, hero_filter="nevermore")
```

**Returns:**
```json
[
  {
    "game_time": 140.5,
    "game_time_str": "2:20",
    "hero": "nevermore",
    "target": "npc_dota_neutral_centaur_khan",
    "damage": 85,
    "camp_type": "large",
    "near_lane": "mid"
  }
]
```

**Use for:**

- "Who was farming neutrals during laning?"
- "Did the support pull the lane?"
- "How much did SF farm neutrals mid?"

**Camp Types:**

| Type | Description |
|------|-------------|
| `small` | Small camps (kobolds, hill trolls) |
| `medium` | Medium camps (wolves, ogres, harpies) |
| `large` | Large camps (centaurs, satyrs, hellbears) |
| `ancient` | Ancient camps (black dragons, thunderhides) |

!!! tip "Pull Detection"
    Events with `near_lane` set indicate the hero was near a lane when attacking neutrals - this often indicates pull attempts by supports.

---

### get_tower_pressure

Get all tower damage taken by heroes during laning phase.

```python
tower_events = lane_svc.get_tower_pressure(parsed_data, hero_filter="naga_siren")
```

**Returns:**
```json
[
  {
    "game_time": 85.0,
    "game_time_str": "1:25",
    "tower": "npc_dota_goodguys_tower1_bot",
    "hero": "naga_siren",
    "damage": 230,
    "tower_team": "radiant",
    "lane": "bot"
  }
]
```

**Use for:**

- "Who took the most tower aggro?"
- "Was the offlaner diving tower?"
- "How much tower damage did the carry take?"

!!! note "Tower Aggro Analysis"
    High tower damage in laning phase often indicates:

    - Offlaner playing aggressively (normal)
    - Carry being pushed under enemy tower (lane lost)
    - Dive attempts by supports or mid

---

## Lane Analysis Example Queries

**"Who won each lane?"**
```python
summary = get_lane_summary(match_id=8461956309)
# Returns: top_winner, mid_winner, bot_winner
```

**"How did the carry's lane go?"**
```python
summary = get_lane_summary(match_id=8461956309)
carry = next(h for h in summary.hero_stats if h.role == "core" and h.team == "radiant")
# Check: last_hits_10min, damage_received, time_under_own_tower
```

**"Did the support rotate mid?"**
```python
summary = get_lane_summary(match_id=8461956309)
mid_rotations = [r for r in summary.rotations if r.to_lane == "mid"]
```

**"Was the wave pushed into tower?"**
```python
tower_events = lane_svc.get_tower_proximity_timeline(data, hero_filter="antimage")
# Track entered/left events to see lane equilibrium
```

**"Did the support pull the lane?"**
```python
summary = get_lane_summary(match_id=8461956309)
support = next(h for h in summary.hero_stats if h.role == "support" and h.lane == "bot")
# Check: pull_attempts, neutral_attacks
```

**"Who was farming neutrals mid?"**
```python
summary = get_lane_summary(match_id=8461956309)
mid_neutral_aggro = [na for na in summary.neutral_aggro if na.near_lane == "mid"]
# Group by hero to see who farmed most
```

**"Who took the most tower damage?"**
```python
summary = get_lane_summary(match_id=8461956309)
# Sort hero_stats by tower_damage_taken
most_tower_damage = max(summary.hero_stats, key=lambda h: h.tower_damage_taken)
```

**"Show me the carry's first 3 waves"**
```python
from src.services.lane.lane_service import LaneService

lane_svc = LaneService()
waves = lane_svc.get_lane_waves(data, lane="bot", team="dire", hero_filter="juggernaut")
for wave in waves[:3]:
    print(f"Wave {wave.wave_number}: {wave.total_deaths} CS")
    # Wave 1: 3 CS, Wave 2: 4 CS, Wave 3: 2 CS
```

**"Compare wave-by-wave efficiency"**
```python
waves = lane_svc.get_lane_waves(data, lane="bot", team="dire", hero_filter="juggernaut")
total_possible = len(waves) * 4  # 4 creeps per wave
total_cs = sum(w.total_deaths for w in waves)
efficiency = total_cs / total_possible * 100
# "Juggernaut got 85% of possible lane CS"
```

---

## Data Limitations

**Currently NOT trackable from replay data:**

| Data | Status | Why |
|------|--------|-----|
| Tower damage on creeps | Missing | Combat log doesn't include tower-to-creep damage |
| Creep-on-creep damage | Missing | Only hero interactions logged |
| Creep entity positions | Missing | Only hero positions tracked in entities |
| Creep entity IDs | Missing | Combat log uses generic names like `npc_dota_creep_goodguys_melee` |
| Lane equilibrium position | Derived | Approximated via tower proximity |
| Stack count detection | Partial | Can count clears but not stacks created |

!!! tip "Lane Equilibrium Analysis"
    While exact creep positions aren't available, you can analyze lane equilibrium through:

    - **Tower proximity timeline**: Time spent under own vs enemy tower
    - **Wave nuke detection**: When heroes push the wave
    - **Hero position at CS**: Where last hits occurred
    - **Harass patterns**: Trading forces lane to push/pull
