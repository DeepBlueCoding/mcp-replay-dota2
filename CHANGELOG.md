## v1.1.0-dev3 (2025-12-16)

### Feat

- **python-manta 1.4.7.1.dev1**: Upgrade with attack collector and hero naming fixes
  - Fixed hero naming: proper camelToSnake conversion (`shadow_demon` not `shadow__demon`)
  - New melee attack tracking from combat log DAMAGE events
  - Unified AttackEvent model for ranged and melee attacks
  - ~32,000 attack events per match for complete last-hit analysis

### Refactor

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

### Fix

- Hero names now consistent across entity snapshots and combat log (python-manta fix)

---

## v1.1.0-dev2 (2025-12-16)

### Feat

- **OpenDota SDK 7.40.1 field integration**:
  - `get_match_heroes`: Added `rank_tier`, `teamfight_participation`, `stuns`, `camps_stacked`, `obs_placed`, `sen_placed`, `lane_efficiency`, `item_neutral2`
  - `get_match_players`: Added `rank_tier` field
  - `get_match_info`: Added `league` object, `pre_game_duration`, `comeback`, `stomp`, team `logo_url`
  - `get_match_draft`: Added `draft_timings` array with pick/ban timing data
  - `get_lane_summary`: Added `lane_efficiency` to hero stats

### Test

- **New tests for OpenDota SDK 7.40.1 fields** in `test_match_fetcher.py`:
  - `TestOpenDotaSDK740Fields`: 10 tests for new player fields
  - `TestEnhancedMatchInfo`: 7 async tests for enhanced match info

### Refactor

- **Test suite converted to real match data validation**:
  - `test_fight_analyzer.py`: Rewritten from ~1247 lines of mock events to ~366 lines testing actual fight patterns from match 8461956309
  - `test_rotation_service.py`: Converted from synthetic data tests to real rotation analysis (24 rotations in match 1, 36 in match 2)
  - `test_model_validation.py`: Changed from Pydantic type validation to testing actual service outputs with real values
  - Tests now verify actual match data: deaths, item purchases, rune pickups, objectives, fights, lane stats, rotations

### Test

- **Match 8461956309 verified data points**:
  - 31 hero deaths, first blood Earthshaker by Disruptor at 4:48
  - 19 rune pickups, Naga Siren arcane at 6:15
  - 4 Roshan kills, 14 tower kills (first: Dire mid T1 at 11:09)
  - 24 fights, 24 rotations (Shadow Demon most active with 6)
  - Lane winners: Dire top, Radiant mid, Radiant bot
  - Juggernaut 63 LH@10, Nevermore 105 LH@10

- **Match 8594217096 verified data points**:
  - 53 game deaths, first blood Batrider by Pugna at 1:24
  - 3 Roshan kills, 14 towers, 5 courier kills
  - 36 rotations (Juggernaut most active)

## v1.0.9 (2025-12-12)

### Fix

- fix get_match_info and get_match_draft returning "Could not parse" errors
- propagate actual exceptions instead of swallowing with generic error messages
- fix league_name filter in get_pro_matches to use bidirectional matching (e.g., "Blast Slam V" now finds "SLAM V")

## v1.0.6.dev2 (2025-12-11)

### Fix

- use PEP 440 pre-release detection for TestPyPI vs PyPI

## v1.0.5 (2025-12-11)

### Feat

- add position (1-5) assignment and draft context to match tools
- add ability_filter to get_raw_combat_events and get_hero_performance
- add detail_level parameter for combat log token control
- add get_hero_combat_analysis tool for per-hero combat stats

### Fix

- count abilities across entire match, not just during fights
- add NOT FOR HERO PERFORMANCE warnings to competing tools
- blend team-specific and proMatches data for better coverage
- reduce combat log max_events caps and improve docstrings

### Refactor

- rename tools for clearer LLM selection

## v1.1.0 (2025-12-08)

### Feat

- add counter picks to get_match_heroes tool
- hero counter picks database for draft analysis
- combat-intensity fight detection and highlight improvements

### Fix

- correct field mappings in get_match_heroes (lane, gpm, xpm)

### Refactor

- split MCP tools into domain-specific modules

## v1.0.1 (2025-12-08)

## v1.0.0 (2025-12-08)

### Feat

- **pro_scene**: add player signature heroes and role data
- add Pydantic response models with descriptions for all MCP tools
- add fight highlights detection (multi-hero abilities, kill streaks, team wipes)
- upgrade to official PyPI releases and complete v2 migration
- add multi-camp detection and upgrade to python-manta dev12
- migrate to python-manta dev11 consolidated HeroSnapshot API
- add get_farming_pattern and get_rotation_analysis tools
- resolve pro player names from account_id
- add filtering options to get_pro_matches tool
- add Docker support, coaching instructions, and download validation
- cache test replay in CI for faster builds
- add pro scene resources, match info tools, and AI summaries
- add download_replay tool for pre-caching replays

### Fix

- **ci**: skip metadata parsing to avoid OOM in CI
- **ci**: correct parsed replay cache path to match ReplayCache
- **ci**: add pre-parse step to populate replay cache
- **ci**: cache parsed replay data and fix asyncio in conftest
- update test to expect actual game time duration
- use OpenDota SDK generic get() method for API calls
- update python-manta to dev8 and fix rune time test
- use entry.game_time directly instead of tick_to_game_time
- invalidate corrupt replay cache, add size verification
- handle None timeline in conftest fixtures
- cache only raw replay, not parsed data
- cache both replay and parsed data for faster CI
- skip tests when replay file unavailable in CI
- mypy type errors, add CI check requirement to CLAUDE.md
- remove build artifacts, fix lint errors, update gitignore
- resolve ruff lint errors
- use MkDocs Material admonition syntax for AI summaries
- commit constants files for CI
- fix pyproject.toml dependencies and CI workflow

### Refactor

- merge metadata parsing into single-pass replay parse
- migrate to ReplayService as single entry point for replay data
- convert parameterized resources to tools, single-pass parsing
