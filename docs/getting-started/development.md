# Development Guide

??? info "🤖 AI Summary"

    Development setup and testing guide. All tests use real match data from two pro matches (8461956309 and 8594217096). CI caches replay files and parsed data for fast test execution (~2 minutes). Tests verify actual service outputs against known match values.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/DeepBlueCoding/mcp-replay-dota2.git
cd mcp-replay-dota2
uv sync

# Run tests (requires replay files)
uv run pytest

# Run CI pipeline
uv run ruff check src/ tests/ dota_match_mcp_server.py
uv run mypy src/ dota_match_mcp_server.py --ignore-missing-imports
uv run pytest
```

## Test Replay Files

Tests require two replay files in `~/dota2/replays/`:

| Match ID | Description | File |
|----------|-------------|------|
| 8461956309 | Primary test match | `8461956309.dem` |
| 8594217096 | Secondary test match (OG game) | `8594217096.dem` |

Download replays via the MCP server's `download_replay` tool or manually from OpenDota/Dotabuff.

---

## Testing Philosophy

All tests validate against **real match data**, not mock/synthetic events. This ensures:

1. **Catch real bugs** - If parsing logic changes, tests fail with actual data
2. **Verify actual values** - Tests assert specific deaths, items, fights from known matches
3. **No false confidence** - Mock tests can pass while production fails

### Test Structure

```
tests/
├── conftest.py              # Session-scoped fixtures, replay caching
├── test_fight_analyzer.py   # Fight detection, highlights (real patterns)
├── test_rotation_service.py # Rotation analysis (real rotations)
├── test_model_validation.py # Service outputs (real values)
├── test_combat_log.py       # Combat log parsing
├── test_lane_service.py     # Lane analysis
├── test_farming_service.py  # Farming patterns
└── ...
```

---

## Test Data Reference

### Match 8461956309 (Primary)

Verified data points used in tests:

| Category | Data |
|----------|------|
| **Deaths** | 31 total, first blood Earthshaker by Disruptor at 4:48 |
| **Runes** | 19 pickups, Naga Siren arcane at 6:15 |
| **Objectives** | 4 Roshan, 14 towers (first: Dire mid T1 at 11:09 by Nevermore) |
| **Fights** | 24 detected |
| **Rotations** | 24 total, Shadow Demon most active (6) |
| **Lanes** | Dire won top, Radiant won mid and bot |
| **CS@10** | Juggernaut 63, Nevermore 105 |
| **Lane Scores** | Radiant 251.5, Dire 237.5 |

**Fight Highlights Verified**:

- Fissure hitting 2 heroes at 6:06
- Echo Slam hitting 4 heroes at 46:45
- Requiem hitting 4 heroes at 46:45
- Earthshaker double kill at 46:45
- BKB+Blink combo (ES initiator) at 38:27
- Coordinated ES+Nevermore ults at 38:27
- Medusa Outworld Staff save at 38:27

### Match 8594217096 (Secondary)

| Category | Data |
|----------|------|
| **Deaths** | 53 game deaths, first blood Batrider by Pugna at 1:24 |
| **Objectives** | 3 Roshan, 14 towers, 5 couriers |
| **Rotations** | 36 total, Juggernaut most active |

---

## CI Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
jobs:
  test:
    steps:
      - Restore replay cache (~/dota2/replays/)
      - Restore parsed data cache (~/.cache/mcp_dota2/parsed_replays_v2/)
      - Run ruff lint
      - Run mypy type check
      - Run pytest
      - Save caches
```

### Cache Strategy

- **Replay files**: Cached in CI, ~150MB per replay
- **Parsed data**: Cached to skip re-parsing, instant test startup
- **Cache key**: Based on test match IDs

---

## Adding New Tests

### 1. Use Real Data

```python
def test_something_real(self, combat_service, parsed_replay_data):
    """Test with actual match data."""
    deaths = combat_service.get_hero_deaths(parsed_replay_data)

    # Assert ACTUAL values from the match
    assert len(deaths) == 31
    assert deaths[0].victim == "earthshaker"
    assert deaths[0].killer == "disruptor"
```

### 2. Never Use Synthetic Events

```python
# ❌ BAD - Mock data can hide real bugs
def test_with_mock():
    fake_events = [CombatLogEvent(...)]  # Synthetic
    result = process(fake_events)
    assert result.success  # Passes but doesn't test real parsing

# ✅ GOOD - Real data catches actual issues
def test_with_real(self, parsed_replay_data):
    result = service.process(parsed_replay_data)
    assert result.deaths == 31  # Actual value from match
```

### 3. Use Session-Scoped Fixtures

```python
# conftest.py provides parsed data once per test session
@pytest.fixture(scope="session")
def parsed_replay_data():
    rs = ReplayService()
    return asyncio.run(rs.get_parsed_data(TEST_MATCH_ID))

# Tests reuse the same parsed data
def test_feature_a(self, parsed_replay_data):
    ...

def test_feature_b(self, parsed_replay_data):
    ...  # Same data, no re-parsing
```

---

## Running Specific Tests

```bash
# Run single test file
uv run pytest tests/test_fight_analyzer.py -v

# Run specific test class
uv run pytest tests/test_rotation_service.py::TestMatch8461956309Rotations -v

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run fast tests only (no replay parsing)
uv run pytest -m fast
```

---

## Common Issues

### Missing Replay Files

```
SKIPPED - Replay file not available (run locally with replay)
```

**Solution**: Download replays to `~/dota2/replays/` or run CI with cached replays.

### Slow Tests

First run parses replays (~30s each). Subsequent runs use cache (~3s total).

### Test Value Mismatch

If a test fails with wrong values, the service logic may have changed. Update tests with new verified values from manual inspection.
