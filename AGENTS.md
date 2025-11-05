# Repository Guidelines

## Project Structure & Module Organization
`src/` holds runtime modules: `resources/` surfaces MCP-ready data (for example `heroes_resources.py`), `tools/` wraps FastMCP utilities, and `utils/` provides shared helpers for constants, fuzzy search, and replays. Root scripts (`dota_match_mcp_server.py`, `main.py`) are the entry points; data caches and artifacts live in `data/`, while maintenance helpers (like `scripts/fetch_constants.py`) keep them current. Primary tests live in `tests/`, and pytest still collects legacy root files such as `test_fuzzy_search.py`.

## Build, Test, and Development Commands
```
uv sync                                  # install pinned Python 3.12 environment
uv run python dota_match_mcp_server.py   # launch the stdio FastMCP server
uv run python main.py                    # smoke test the package entry point
uv run pytest                            # execute the suite with pytest.ini settings
uv run python scripts/fetch_constants.py # refresh dotaconstants caches in data/
```
Use `uv run` so imports resolve inside the managed venv.

## Coding Style & Naming Conventions
Stick to 4-space indentation, type hints, and docstrings as shown in `src/utils/hero_fuzzy_search.py`. Prefer `snake_case` functions, `CapWords` classes, and `SCREAMING_SNAKE_CASE` constants (see `src/utils/constants.py`). Keep FastMCP resource IDs in the `dota2://` namespace, ensure regenerated JSON stays lowercase_with_underscores, and wire any formatter or linter through `pyproject.toml` so it can run via `uv run`.

## Testing Guidelines
`pytest.ini` scopes discovery to `tests/` plus `test_*.py`, enables verbose output, short tracebacks, and strict marker validation. Mirror the production layout for new tests (e.g., `tests/test_heroes_resources.py`), quarantine replay fixtures under `data/fixtures/`, and tag network- or replay-heavy suites with `@pytest.mark.integration` or `@pytest.mark.slow`. Gate those locally through `uv run pytest -m "not slow"` and favor assertions that validate hero IDs, alias coverage, and replay parsing results.

## Commit & Pull Request Guidelines
With no public history yet, adopt Conventional Commits (`feat:`, `fix:`, `docs:`) to keep the log searchable. PRs should describe the gameplay or tooling scenario affected, list exact verification commands and required data, and link any tracking issue. Mention if `scripts/fetch_constants.py` was run so reviewers expect large JSON diffs, and keep commits small enough that the MCP server plus tests stay green after every push.

## Data Refresh & Security Notes
Do not commit raw Valve replays; store only derived metadata and reference paths in `data/README.md` when necessary. After refreshing hero metadata, inspect diffs in `data/heroes*.json` to confirm canonical IDs remain stable because `HeroFuzzySearch` depends on them. Keep OpenDota or Manta tokens in your shell environment (for example `export MANTA_API_KEY=...`) and document any newly required variable here instead of tracking `.env` files.
