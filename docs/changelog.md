# Changelog

??? info "🤖 AI Summary"

    Project changelog following Keep a Changelog format. v1.0.0 release includes: MCP resources (heroes, map, pro scene), 30+ MCP tools for match analysis, replay parsing with python-manta, fight detection with highlights, farming pattern analysis, rotation tracking, pro scene integration with fuzzy search.

All notable changes to this project will be documented in this file.

## [1.1.0-dev7] - 2025-12-28

### Added

- **Position-Specific Analysis Frameworks** - Comprehensive coaching personas loaded from `data/personas/`:
  - **`coaching_persona.md`** - Senior analyst persona with TI qualifier/11k MMR background
  - **`pos1_carry.md`** - Complete Position 1 Carry analysis framework:
    - Laning phase: equilibrium management, lane dynamics, exit timing
    - Farming phase: wave-camp cycling, timer awareness, item benchmarks
    - Transition: active vs passive farming, fight selection, grouping
    - Closing: Aegis usage, no-throw mentality, objective priority
  - Framework extensible for positions 2-5

- **`src/coaching/personas.py`** - Persona loader module:
  - `get_coaching_persona()` - Loads main coaching persona
  - `get_position_framework(position)` - Loads position-specific framework
  - `lru_cache` for efficient file loading
  - Graceful fallback for missing files

- **Professional Coaching Framework** - Comprehensive coaching prompts overhaul:
  - **LANE_RECOVERY** - Framework for analyzing recovery when lanes are lost
  - **LATE_GAME_FRAMEWORK** - Framework for 30+ minute analysis
  - **Expanded COMMON_MISTAKES** - Added strategic mistakes and late game categories

### Changed

- **Coaching prompts refactored** - Now load personas from files instead of inline constants
- **`get_hero_performance_prompt`** - Includes position-specific framework when available
- **FIGHT_ANALYSIS restructured** - Now uses before/during/after framework
- **Sampling prompts updated** - All functions use loaded personas

### Docs

- **Updated coaching.md** - Documents persona system, position frameworks, carry-specific analysis

---

## [1.1.0-dev6] - 2025-12-28

### Added

- **`delete_replay` tool** - New tool for manual cache management:
  - Deletes both replay file and parsed cache for a match
  - Use when automatic retry fails or cached data appears incorrect
  - Returns status indicating what was deleted (`file_deleted`, `cache_deleted`)

### Fixed

- **Automatic retry for corrupt replays** - `download_replay` now handles corruption gracefully:
  - When parsing fails, automatically deletes corrupt file and clears cache
  - Retries download and parse once before failing
  - Clear error messages on permanent failure

## [1.1.0-dev5] - 2025-12-27

### Added

- **Draft lane assignment** - Added `lane` field to `DraftAction` for correct lane matchup analysis:
  - `lane` field derived from `position`: pos 1/5 → `safelane`, pos 2 → `mid`, pos 3/4 → `offlane`
  - Enables LLMs to correctly construct lane matchups (e.g., carry+hard support vs offlane+soft support)
  - Bans have `lane: null` (no lane assignment for banned heroes)

- **HeroStats expected_lane** - Added `expected_lane` field to distinguish theoretical vs actual lanes:
  - `lane`: Actual lane played (from OpenDota laning detection)
  - `expected_lane`: Theoretical lane based on position (pos1/5=safelane, pos2=mid, pos3/4=offlane)
  - Helps LLMs detect trilanes and unusual lane setups (e.g., Naga pos4 expected offlane but played safelane trilane)

- **League fuzzy search** - Added fuzzy matching for `league_name` filter in `get_pro_matches`:
  - "TI 2025" now matches "The International 2025"
  - "ESL" matches "ESL One Kuala Lumpur"
  - "DPC" matches "Dota Pro Circuit"
  - "blast" matches "BLAST Slam V"
  - Common abbreviations: TI, ESL, DPC, dreamleague, blast, slam, riyadh, bali

### Fixed

- **Position assignment uses lane, not GPM** - Fixed pos 4/5 assignment:
  - OLD (wrong): Higher GPM support = pos 4, lower = pos 5
  - NEW (correct): Offlane support (lane_role=3) = pos 4, Safelane support (lane_role=1) = pos 5
  - Fixes Naga pos 5 (safelane support) being wrongly assigned pos 4 due to high late-game GPM
  - Fixes Disruptor pos 4 (offlane brawler) being wrongly assigned pos 5 due to low GPM
- **Prompt scope discipline** - `analyze_draft` prompt now focuses only on draft analysis:
  - Covers: lane matchups, synergies, counters, weaknesses, ban analysis, grade
  - Explicitly excludes: teamfight combos, item timings, game predictions
  - Clear instruction: "Do NOT analyze teamfight execution, item builds, or make game predictions"
- **Constants loading defensive check** - Prevents NoneType errors when constants fail to load

### Test

- **New tests for lane field**:
  - `TestDraftActionLaneField`: 7 tests for lane field derivation from position
  - `TestGetLaneFromPosition`: 7 tests for `_get_lane_from_position` helper
  - `TestHeroStatsExpectedLane`: 4 tests for expected_lane field in HeroStats
- **Updated position assignment tests**:
  - `test_pos4_is_offlane_support`: Verifies pos 4 has lane_role=3 (offlane)
  - `test_pos5_is_safelane_support`: Verifies pos 5 has lane_role=1 (safelane)
  - `test_dire_naga_is_pos5_safelane_support`: Naga (high GPM) correctly assigned pos 5
  - `test_dire_disruptor_is_pos4_offlane_support`: Disruptor correctly assigned pos 4
- **New tests for prompts** (`tests/prompts/test_mcp_prompts.py`):
  - `TestAnalyzeDraftPrompt`: 11 tests verifying draft-only focus, excludes teamfight/items
  - `TestReviewHeroPerformancePrompt`: 3 tests for coaching sections
  - `TestAnalyzeDeathsPrompt`: 2 tests for 5-question framework
  - `TestAnalyzeTeamfightPrompt`: 2 tests for teamfight analysis sections
  - `TestPromptRegistration`: 2 tests verifying all 7 prompts registered
- **New tests for league fuzzy search** (`tests/utils/test_league_fuzzy_search.py`):
  - `TestLeagueAliasExpansion`: 4 tests for alias expansion (TI, ESL, DPC, blast)
  - `TestLeagueMatchesFilter`: 10 tests for fuzzy matching logic
  - `TestPGLWallachiaMatching`: 7 tests for PGL Wallachia tournament matching
  - `TestLeagueSearch`: 4 tests for initialized search functionality

### Docs

- **New prompts documentation** (`docs/api/prompts.md`):
  - Full reference for all 7 prompts with parameter tables
  - Analysis sections each prompt covers
  - Usage examples with Claude Code and MCP SDK
- **Added `get_tournament_series` to pro-scene docs** - Tournament bracket/series analysis tool
- **Added `get_client_capabilities` diagnostic tool** - Check MCP client sampling support
- **Added Prompts to mkdocs nav** - Prompts reference now accessible from sidebar

---

## [1.1.0-dev4] - 2025-12-18

### Added

- **Version-aware map data** - GameContext refactor for patch-specific analysis:
  - `GameContext` dataclass encapsulates version-specific data from parsed replays
  - `GameContext.from_parsed_data()` factory method creates context from replay data
  - `PositionClassifier` class uses `MapData` for version-aware position classification
  - `LaneBoundary` model defines lane regions (x_min, x_max, y_min, y_max)
  - Lane boundaries added to `map_data.json` for patches 7.33, 7.37, 7.38, 7.39
  - Fallback to `DEFAULT_LANE_BOUNDARIES` when no GameContext provided

- **Versioned map data files**:
  - `data/versions/patches/{version}/map_data.json` for each supported patch
  - `VersionedMapData` provider with fallback to latest known version
  - All patches include `lane_boundaries` for lane classification

### Changed

- **Services updated to accept GameContext**:
  - `CombatService.get_hero_deaths()` - Position classification uses version-aware boundaries
  - `CombatService.get_courier_kills()` - Position classification uses version-aware boundaries
  - `FarmingService.get_farming_pattern()` - Lane classification uses GameContext
  - `LaneService` - All methods accept `game_context` parameter
  - `RotationService.get_rotation_analysis()` - Lane assignments use version-aware boundaries

- **MCP tools create GameContext from replays**:
  - `get_hero_deaths`, `get_courier_kills`, `get_lane_summary`, `get_rotation_analysis`, `get_farming_pattern`
  - Context is created via `GameContext.from_parsed_data(data)` after replay parsing

### Technical

- Renamed `LANE_BOUNDARIES` to `DEFAULT_LANE_BOUNDARIES` in LaneService and RotationService
- Added `_get_lane_boundaries()` helper pattern to services for boundary extraction
- `TYPE_CHECKING` import pattern used for GameContext to avoid circular imports

---

## [1.1.0-dev3] - 2025-12-16

### Added

- **python-manta 1.4.7.1.dev1** - Upgrade with attack collector and hero naming fixes:
  - Fixed hero naming: proper camelToSnake conversion (`shadow_demon` not `shadow__demon`)
  - New melee attack tracking from combat log DAMAGE events
  - Unified `AttackEvent` model for ranged and melee attacks
  - ~32,000 attack events per match for complete last-hit analysis

### Changed

- **Test suite restructured to mirror source hierarchy**:
  - `tests/services/combat/` - CombatService tests
  - `tests/services/farming/` - FarmingService tests
  - `tests/services/lane/` - LaneService tests
  - `tests/services/rotation/` - RotationService tests
  - `tests/services/analyzers/` - FightAnalyzer tests
  - `tests/examples/` - Match-specific validation tests
  - `tests/models/` - Pydantic model tests
  - `tests/resources/` - Resource tests
  - `tests/utils/` - Utility tests

### Fixed

- Hero names now consistent across entity snapshots and combat log (python-manta fix)

---

## [1.1.0-dev2] - 2025-12-16

### Added

- **OpenDota SDK 7.40.1 field integration** - New player/match metrics:
  - `get_match_heroes`: Added `rank_tier`, `teamfight_participation`, `stuns`, `camps_stacked`, `obs_placed`, `sen_placed`, `lane_efficiency`, `item_neutral2`
  - `get_match_players`: Added `rank_tier` field
  - `get_match_info`: Added `league` object (league_id, name, tier), `pre_game_duration`, `comeback`, `stomp`, and `logo_url` in team objects
  - `get_match_draft`: Added `draft_timings` array with pick/ban timing data (order, extra_time, total_time_taken)
  - `get_lane_summary`: Added `lane_efficiency` to hero stats

- **New Pydantic models**:
  - `DraftTiming`: Draft timing data for each pick/ban
  - `LeagueInfo`: League information with tier
  - Updated `TeamInfo` with `logo_url`
  - Updated `MatchInfoResult` with `league`, `comeback`, `stomp`, `pre_game_duration`

- **New tests for OpenDota SDK 7.40.1 fields** in `test_match_fetcher.py`:
  - `TestOpenDotaSDK740Fields`: 10 tests for new player fields
  - `TestEnhancedMatchInfo`: 7 async tests for enhanced match info

### Refactored

- **Test suite converted to real match data validation**:
  - `test_fight_analyzer.py`: Rewritten from ~1247 lines of mock events to ~366 lines testing actual fight patterns
  - `test_rotation_service.py`: Converted from synthetic data tests to real rotation analysis
  - `test_model_validation.py`: Changed from Pydantic type validation to testing actual service outputs
  - All tests now verify real match data instead of mock/synthetic events

### Test Coverage

- **Match 8461956309 (primary test match)**:
  - 31 hero deaths, first blood Earthshaker by Disruptor at 4:48
  - 19 rune pickups, Naga Siren arcane at 6:15
  - 4 Roshan kills, 14 tower kills (first: Dire mid T1 at 11:09)
  - 24 fights detected, 24 rotations (Shadow Demon most active with 6)
  - Lane analysis: Dire won top, Radiant won mid and bot
  - CS verification: Juggernaut 63 LH@10, Nevermore 105 LH@10
  - Fight highlights: Echo Slam 4 heroes at 46:45, ES double kill, BKB+Blink combos

- **Match 8594217096 (secondary test match)**:
  - 53 game deaths, first blood Batrider by Pugna at 1:24
  - 3 Roshan kills, 14 tower kills, 5 courier kills
  - 36 rotations detected (Juggernaut most active)

---

## [1.0.9] - 2025-12-12

### Fixed

- **get_match_info and get_match_draft** returning generic "Could not parse" errors
- Exception handling now propagates actual error messages instead of swallowing with generic messages
- **get_pro_matches league_name filter** now uses bidirectional matching (e.g., "Blast Slam V" finds "SLAM V")

## [1.2.0] - 2025-12-11

### Added

- **Position (1-5) assignment** for all match tools:
  - `get_match_heroes`, `get_match_players`, `get_match_draft` now include `position` field
  - Position determined from OpenDota lane data (`lane_role`) and GPM:
    - **Pos 1** = Safelane core (lane_role=1, highest GPM)
    - **Pos 2** = Mid (lane_role=2)
    - **Pos 3** = Offlane core (lane_role=3, highest GPM)
    - **Pos 4** = Soft support (higher GPM support)
    - **Pos 5** = Hard support (lowest GPM support)
  - Fixes LLM incorrectly guessing positions (e.g., Axe as pos5 instead of pos3)

- **Draft context data** in `get_match_draft` picks:
  - `counters`: Heroes that counter this pick (bad matchups)
  - `good_against`: Heroes this pick counters (favorable matchups)
  - `when_to_pick`: Conditions when this hero is strong
  - Helps LLM understand draft decisions and counter-picking

### Changed

- `assign_roles()` renamed to `assign_positions()` in match_fetcher.py
- `DraftAction` model now includes `position`, `counters`, `good_against`, `when_to_pick` fields
- `HeroStats` and `MatchPlayerInfo` models now include `position` field

---

## [1.1.4] - 2025-12-11

### Changed

- **`get_pro_matches` tool** - Enhanced team filtering with head-to-head support:
  - Renamed `team_name` parameter to `team1_name`
  - Added `team2_name` parameter for head-to-head filtering
  - **Single team filter** (`team1_name` only): Returns all matches involving that team
  - **Head-to-head filter** (`team1_name` + `team2_name`): Returns only matches where both teams played against each other, regardless of radiant/dire side
  - Combine with `league_name`, `tier`, and `days_back` for deep filtering (e.g., Spirit vs OG at The International)

---

## [1.1.3] - 2025-12-10

### Added

- **`ability_filter` parameter** for focused ability analysis:
  - `get_raw_combat_events`: Filter combat log by specific ability (e.g., "ice_path", "chronosphere")
  - `get_hero_performance`: Filter ability summary and per-fight abilities by name
  - Case-insensitive partial matching (e.g., "fissure" matches "earthshaker_fissure")

### Changed

- **Tool renames for clarity** (LLM routing improvement):
  - `get_combat_log` → `get_raw_combat_events` (emphasizes raw event debugging)
  - `get_hero_combat_analysis` → `get_hero_performance` (clearer purpose)

- **Added routing hints** to competing tools:
  - `get_hero_deaths`, `list_fights`, `get_teamfights`, `get_rotation_analysis` now include "NOT FOR HERO PERFORMANCE QUESTIONS → Use get_hero_performance instead" in docstrings

### Fixed

- **Ability counting now covers entire match** - Previously only counted abilities used during detected fights; now counts ALL ability usage across the entire match with per-fight breakdown preserved

---

## [1.1.2] - 2025-12-09

### Added

- **`detail_level` parameter** for combat log tools - Controls token usage (~98% reduction with `narrative`):
  - `narrative` (default): Deaths, abilities, items, purchases, buybacks (~500-2,000 tokens)
  - `tactical`: Adds hero-to-hero damage and debuffs (~2,000-5,000 tokens)
  - `full`: All events including creeps (~50,000+ tokens, debugging only)
  - Applied to `get_combat_log` and `get_fight_combat_log` tools
  - `max_events` parameter added (default 500, max 2000) to prevent overflow
  - `truncated` field in response indicates if results were capped

### Changed

- **Removed `significant_only` parameter** - Replaced by `detail_level` enum for finer control
- Default behavior now uses `narrative` detail level (was equivalent to `significant_only=True`)

---

## [1.1.1] - 2025-12-08

### Added

- **`get_hero_combat_analysis` tool** - Per-hero combat performance analysis across all fights:
  - Tracks kills, deaths, assists per fight
  - Ability usage with hit rates (total casts vs hero hits)
  - Damage dealt and received per fight
  - Teamfight vs skirmish classification
  - **Ground-targeted ability tracking**: Ice Path, Fissure, etc. track hits via MODIFIER_ADD events (stun debuffs applied)
  - Hit rate can exceed 100% for AoE abilities hitting multiple heroes per cast
  - Aggregate stats across all fights for the hero

---

## [1.1.0] - 2025-12-08

### Changed

- **Major refactor: Tools split into domain-specific modules** (92% code reduction in main entry point)
  - `dota_match_mcp_server.py`: 2606 → 206 lines
  - New `src/tools/` directory with modular tool registration:
    - `replay_tools.py` - Replay download tool
    - `combat_tools.py` - Deaths, combat log, objectives, runes, couriers
    - `fight_tools.py` - Fight detection, teamfights, fight replay
    - `match_tools.py` - Match info, timeline, draft, heroes, positions
    - `pro_scene_tools.py` - Pro players, teams, leagues, matches
    - `analysis_tools.py` - Jungle, lane, farming patterns, rotations
  - Service injection pattern via `register_all_tools(mcp, services)` coordinator
  - No functional changes - all 30+ tools work identically

### Technical

- Clean separation of concerns: each tool module handles one domain
- Services dictionary pattern for dependency injection
- Easier maintenance and testing of individual tool groups

---

## [1.0.4] - 2025-12-08

### Added

- **Hero counter picks database** integrated into `/heroes` resource:
  - 848 counter matchups with mechanical explanations (WHY a hero counters another)
  - 438 favorable matchups (heroes each hero is good against)
  - 529 "when_to_pick" conditions describing optimal draft situations
  - Curated data based on game mechanics: BKB-piercing, silences, roots, mana burn, Blademail, saves, mobility

- New fields in `dota2://heroes/all` resource:
  - `counters`: List of heroes that counter this hero with reasons
  - `good_against`: List of heroes this hero counters with reasons
  - `when_to_pick`: Draft conditions when the hero is strong

- Pydantic models for counter data in `src/models/hero_counters.py`:
  - `CounterMatchup`, `HeroCounters`, `HeroCountersDatabase`
  - `CounterPickResponse`, `DraftCounterAnalysis`, `DraftAnalysisResponse`

- `HeroesResource` methods for counter data access:
  - `get_hero_counters(hero_id)`: Get counter data for a specific hero
  - `get_all_hero_counters()`: Get all hero counter data

- `get_match_heroes` tool now includes counter picks for each hero:
  - Enables draft analysis directly from match data
  - Each hero includes counters, good_against, when_to_pick

### Changed

- `dota2://heroes/all` now includes counter picks data for draft analysis
- `get_match_heroes` enriched with counter picks for draft analysis
- Updated documentation with counter picks examples

---

## [1.0.3] - 2025-12-08

### Added

- **Combat-intensity based fight detection** - Major refactor of fight detection algorithm:
  - Fights are now detected based on hero-to-hero combat activity, not just deaths
  - Catches teamfights where teams disengage before anyone dies
  - Properly captures fight initiation phase (BKB+Blink) before first death
  - Uses intensity-based windowing to separate distinct engagements
  - Filters out harassment/poke (brief exchanges that aren't real fights)
  - New `detect_fights_from_combat()` and `get_fight_at_time_from_combat()` methods

- Extended fight highlight detection with new patterns:
  - **BKB + Blink combos**: Detects BKB + Blink → Big Ability (either order), marks first as initiator, rest as follow-ups
  - **Coordinated ultimates**: Detects when 2+ heroes from the **same team** use big teamfight abilities within 3 seconds. Includes `team` field (radiant/dire)
  - **Refresher combos**: Detects when a hero uses Refresher to double-cast an ultimate
  - **Clutch saves**: Detects self-saves (Outworld Staff, Aeon Disk) and ally saves (Glimmer Cape, Lotus Orb, Force Staff, Shadow Demon Disruption)
  - Self-save detection includes tracking what ability the hero was saved FROM (e.g., Omnislash)

- New data models in `combat_data.py`:
  - `BKBBlinkCombo`: BKB + Blink combo with `is_initiator` flag
  - `CoordinatedUltimates`: Multiple heroes ulting together with `team` field and window tracking
  - `RefresherCombo`: Refresher double ultimate with cast times
  - `ClutchSave`: Save detection with saver, save type, and ability saved from
  - `CombatWindow`: Internal dataclass for combat-intensity based fight detection

- Added `nevermore_requiem` alias to BIG_TEAMFIGHT_ABILITIES (replays use old internal name)

### Changed

- `get_fight_combat_log` now uses combat-based detection by default (captures initiation)
- Fight detection parameters tuned: 8s combat gap, 3s intensity window, 5 min events per window
- Removed `fight_initiator` and `initiation_ability` fields (replaced by `bkb_blink_combos` with `is_initiator` flag)

### Fixed

- Generic AoE detection now properly filters self-targeting (e.g., Echo Slam damaging caster)
- BKB+Blink detection now accepts either order (BKB→Blink or Blink→BKB)
- Clutch saves now require target to be "in danger" (3+ hero damage hits in 2s) to filter false positives
- Hero deaths include position coordinates and location descriptions from entity snapshots
- `significant_only` filter now excludes non-hero deaths (creep kills) from combat events
- Autoattack kills now show `"ability": "attack"` instead of `"dota_unknown"`
- Coordinated ultimates now only detects same-team coordination (was incorrectly grouping opposing team abilities)
- Team hero extraction now correctly finds all 10 heroes by scanning entity snapshots after game start

---

## [1.0.2] - 2025-12-08

### Fixed

- Fixed `get_pro_matches` and `get_league_matches` returning `null` team names
  - OpenDota API doesn't always include team names in match responses
  - Now resolves team names from cached teams data when missing
  - Eliminates need for extra `get_team` tool calls to resolve team names

- Fixed `get_match_heroes` validation error with item fields
  - Items now return human-readable names (e.g., "Blink Dagger") instead of integer IDs
  - Added `get_item_name()` and `convert_item_ids_to_names()` to constants_fetcher
  - Neutral items also converted to display names

### Added

- Model validation tests (`tests/test_model_validation.py`)
  - Tests for HeroStats, MatchHeroesResponse, MatchPlayerInfo validation
  - Tests for item ID to name conversion
  - Ensures Pydantic models reject invalid data types

---

## [1.0.1] - 2025-12-08

### Fixed

- Updated examples documentation to match v1.0.0 Pydantic response models
- Added fight highlights to `get_fight_combat_log` examples (multi_hero_abilities, kill_streaks, team_wipes)
- Fixed `get_farming_pattern` example to use `camp_sequence` and `level_timings`
- Added missing standard fields to all tool response examples

---

## [1.0.0] - 2025-12-08

### Added

#### MCP Resources
- `dota2://heroes/all` - All Dota 2 heroes with stats and abilities
- `dota2://map` - Map geometry with towers, barracks, neutral camps, runes, landmarks
- `dota2://pro/players` - Pro player database with team affiliations
- `dota2://pro/teams` - Pro team database with rosters

#### Match Analysis Tools
- `download_replay` - Pre-cache replay files before analysis (50-400MB files)
- `get_hero_deaths` - All hero deaths with positions and abilities
- `get_combat_log` - Raw combat events with time/hero filters
- `get_fight_combat_log` - Auto-detect fight boundaries with **highlights**:
  - Multi-hero abilities (Chronosphere, Black Hole, Ravage hitting 2+ heroes)
  - Kill streaks (Double kill through Rampage, 18-second window)
  - Team wipes (Aces)
  - Fight initiation detection
- `get_item_purchases` - Item purchase timeline
- `get_objective_kills` - Roshan, tormentors, towers, barracks
- `get_match_timeline` - Net worth, XP, KDA over time for all players
- `get_stats_at_minute` - Snapshot of all players at specific minute
- `get_courier_kills` - Courier snipes with positions
- `get_rune_pickups` - Rune pickup tracking
- `get_match_draft` - Complete draft order for Captains Mode
- `get_match_info` - Match metadata (teams, players, winner, duration)
- `get_match_heroes` - 10 heroes with KDA, items, stats
- `get_match_players` - 10 players with names and hero assignments

#### Game State Tools
- `list_fights` - All fights with teamfight/skirmish classification
- `get_teamfights` - Major teamfights (3+ deaths)
- `get_fight` - Detailed fight information with positions
- `get_camp_stacks` - Neutral camp stacking events
- `get_jungle_summary` - Stacking efficiency by hero
- `get_lane_summary` - Laning phase winners and hero stats (OpenDota integration)
- `get_cs_at_minute` - CS/gold/level at specific minute
- `get_hero_positions` - Hero positions at specific minute
- `get_snapshot_at_time` - High-resolution game state at specific time
- `get_position_timeline` - Hero movement over time range
- `get_fight_replay` - High-resolution replay data for fights

#### Farming & Rotation Analysis
- `get_farming_pattern` - Minute-by-minute farming breakdown:
  - Lane vs jungle creeps, camp type identification
  - Position tracking, key transitions (first jungle, left lane)
  - Summary stats: jungle %, GPM, CS/min, camps by type
- `get_rotation_analysis` - Hero rotation tracking:
  - Rotation detection when heroes leave assigned lane
  - Rune correlation (power runes → rotations)
  - Fight outcomes: kill, died, traded, fight, no_engagement
  - Power/wisdom rune event tracking

#### Pro Scene Features
- `search_pro_player` / `search_team` - Fuzzy search with alias support
- `get_pro_player` / `get_pro_player_by_name` - Player details
- `get_team` / `get_team_by_name` - Team details with roster
- `get_team_matches` - Recent matches for a team
- `get_leagues` / `get_league_matches` - League information
- `get_pro_matches` - Pro matches with filters (tier, team, league, days_back)
- Series grouping for Bo1/Bo3/Bo5 detection
- Player signature heroes and role data

#### Pydantic Response Models
- 40+ typed models with Field descriptions in `src/models/tool_responses.py`
- Timeline: `KDASnapshot`, `PlayerTimeline`, `TeamGraphs`
- Fights: `FightSummary`, `FightHighlights`, `MultiHeroAbility`, `KillStreak`
- Game state: `HeroSnapshot`, `HeroPosition`, `PositionPoint`
- Better IDE autocomplete and documentation

#### Developer Experience
- Comprehensive MkDocs documentation with Material theme
- AI Summary sections on all documentation pages
- Parallel-safe tool hints for LLM optimization
- Server instructions with Dota 2 game knowledge

### Technical

#### Replay Parsing
- Single-pass parsing with python-manta v2 API
- `ReplayService.get_parsed_data(match_id)` as main entry point
- Disk caching via diskcache for parsed replay data
- CDOTAMatchMetadataFile extraction for timeline data

#### Architecture
- Services layer: `CombatService`, `FightService`, `FarmingService`, `RotationService`
- Clean separation: services have no MCP dependencies
- Pydantic models throughout for type safety
