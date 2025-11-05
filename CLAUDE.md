# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Dota 2 Match Analysis MCP Server** built with FastMCP. It provides Model Context Protocol (MCP) tools and resources for analyzing Dota 2 matches using replay files and the OpenDota API. The project focuses on match-specific analysis requiring actual match data.

## Development Commands

### Package Management (CRITICAL)
**ALWAYS use `uv` commands - NEVER use `python` or `pip` directly:**

```bash
# Run Python scripts
uv run python script.py

# Add dependencies
uv add package-name

# Run the MCP server
uv run python dota_match_mcp_server.py
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_heroes_resources.py

# Run without integration tests (those requiring replays/network)
uv run pytest -m "not integration"

# Run with verbose output
uv run pytest -v

# Run specific test function
uv run pytest tests/test_heroes_resources.py::TestHeroesResource::test_get_all_heroes_returns_exact_count
```

### Fetching Dota 2 Constants

```bash
# Fetch all constants from dotaconstants repository
uv run python scripts/fetch_constants.py
```

## Architecture Overview

### Layer Structure

```
MCP Server (dota_match_mcp_server.py)
    ↓
Resources Layer (src/resources/)
    ↓
Utilities Layer (src/utils/)
    ↓
External APIs (OpenDota, dotaconstants, python_manta)
```

### Key Components

#### 1. **MCP Server** (`dota_match_mcp_server.py`)
- FastMCP server exposing tools and resources
- Entry point for MCP clients
- Defines MCP resources (URIs like `dota2://heroes/all`)
- Defines MCP tools (callable functions)

#### 2. **Resources Layer** (`src/resources/`)
- **`heroes_resources.py`**: Core business logic for hero data management
  - Converts dotaconstants format to legacy format
  - Filters heroes by match ID using replay parsing
  - Provides enriched hero data
  - Singleton pattern: `heroes_resource` instance

#### 3. **Utilities Layer** (`src/utils/`)
- **`constants_fetcher.py`**: Downloads and caches constants from odota/dotaconstants
  - Singleton: `constants_fetcher` instance
  - Stores data in `data/constants/`
  - Provides hero/item/ability lookups

- **`replay_downloader.py`**: Downloads and extracts replay files (.dem)
  - Uses OpenDota API to get replay URLs
  - Downloads .bz2 files and extracts to .dem
  - Stores replays in `~/dota2/replays/` by default

- **`hero_fuzzy_search.py`**: Fuzzy hero name matching
  - Uses simplified data from `data/heroes_fuzzy.json`
  - Integrates with constants for full hero data
  - Supports aliases and abbreviations
  - Singleton: `hero_fuzzy_search` instance

#### 4. **Data Storage**
- `data/constants/`: Cached dotaconstants JSON files (heroes, items, abilities, etc.)
- `data/heroes_fuzzy.json`: Simplified hero data for fuzzy search
- `~/dota2/replays/`: Downloaded replay files (*.dem)

### Data Flow Example

**Get Heroes in Match:**
1. MCP client calls `list_match_heroes(match_id)`
2. Server calls `heroes_resource.get_heroes_in_match(match_id)`
3. Resource uses `replay_downloader` to get replay file
4. Resource parses replay with `python_manta.parse_demo_draft()`
5. Resource filters all heroes to only picked heroes
6. Returns filtered hero data in legacy format

### External Dependencies

- **`fastmcp`**: MCP server framework
- **`python-opendota`**: OpenDota API client (local package at `../python-opendota-sdk`)
- **`python-manta`**: Dota 2 replay parser (local package at `../python_manta`)
- **dotaconstants**: Hero/item/ability data from odota/dotaconstants GitHub

## Data Format Conventions

### Hero Data Format

**Legacy Format** (used in MCP responses):
```python
{
    "npc_dota_hero_antimage": {
        "hero_id": 1,
        "canonical_name": "Anti-Mage",
        "aliases": ["anti-mage", "antimage"],
        "attribute": "agility"
    }
}
```

**Dotaconstants Format** (raw from API):
```python
{
    "1": {
        "id": 1,
        "name": "npc_dota_hero_antimage",
        "localized_name": "Anti-Mage",
        "primary_attr": "agi",
        "roles": ["Carry", "Escape"],
        # ... many more fields
    }
}
```

### Attribute Mapping
- `"str"` → `"strength"`
- `"agi"` → `"agility"`
- `"int"` → `"intelligence"`
- `"all"` → `"universal"`

## Testing Philosophy

Following strict Golden Master testing approach:

1. **Test Real Values**: Always use VERIFIED values from actual data
2. **No Framework Testing**: Don't test Pydantic validation or obvious truths
3. **Integration Tests**: Mark tests requiring replays/network with `@pytest.mark.integration`
4. **Golden Master Data**: Use known match IDs with verified hero picks

Example from tests:
```python
REAL_MATCH_ID = 8461956309  # Known match with verified data
EXPECTED_TOTAL_HEROES = 126  # Exact count from dotaconstants
```

## Common Patterns

### Singleton Resources
Most utilities use singleton pattern for reuse:
```python
from src.resources.heroes_resources import heroes_resource
from src.utils.constants_fetcher import constants_fetcher
from src.utils.hero_fuzzy_search import hero_fuzzy_search
```

### Async/Sync Handling
- OpenDota client uses async methods
- Replay downloader provides both async and sync wrappers:
  ```python
  await downloader.download_replay(match_id)  # Async
  downloader.download_replay_sync(match_id)   # Sync wrapper
  ```

### Error Handling
- Functions return empty dicts `{}` on error
- Replay parsing checks `draft_info.success` before proceeding
- Constants loading attempts fetch if not available

## File Naming Conventions

- Test files: `test_*.py` in `tests/` directory
- Resource files: `*_resources.py` in `src/resources/`
- Utility files: descriptive names in `src/utils/`
- Tools: `*_tools.py` in `src/tools/`

## Important Notes

1. **Local Dependencies**: This project depends on two local packages that must exist:
   - `python-opendota-sdk` at `../python-opendota-sdk`
   - `python_manta` at `../python_manta`

2. **Hero Internal Names**: Heroes use `npc_dota_hero_*` format as keys, not IDs or display names

3. **Replay Parsing**: Requires python_manta package with working Rust bindings

4. **Constants Updates**: Run `scripts/fetch_constants.py` to update cached constants from dotaconstants

5. **Match Data**: All match-specific tools require valid match IDs and working replay downloads
