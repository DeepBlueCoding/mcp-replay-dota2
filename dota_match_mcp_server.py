#!/usr/bin/env python3
# ruff: noqa: E402
"""
Dota 2 Match MCP Server - Match-focused analysis

Provides MCP tools for analyzing specific Dota 2 matches using replay files.
All tools require a match_id and work with actual match data.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Add project paths for imports
project_root = Path(__file__).parent.parent
mcp_dir = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(mcp_dir))

from fastmcp import FastMCP

# Import coaching constants for server instructions
from src.coaching.prompts import ANALYSIS_WORKFLOW, COACHING_PERSONA, CORE_PHILOSOPHY

# Tool selection and rules (server-specific)
TOOL_INSTRUCTIONS = """
## Tool Selection

| Question Type | Use This Tool |
|---------------|---------------|
| Hero performance, kills, deaths, ability usage | `get_hero_performance` (with ability_filter if needed) |
| Match winner, duration, teams, players | `get_match_info` |
| Global death timeline, first blood, death counts | `get_hero_deaths` |
| Event-by-event fight breakdown at specific time | `get_fight_combat_log` |
| Laning phase stats, CS comparisons | `get_lane_summary` |
| Item purchase timings | `get_item_purchases` |
| Roshan, towers, barracks kills | `get_objective_kills` |

## Key Rules

1. **get_hero_performance is comprehensive** - Returns kills, deaths, assists, ability stats,
   AND per-fight breakdowns. One call is usually sufficient for hero questions.

2. **One tool per question** - Avoid chaining tools. Each tool returns complete data for its purpose.

3. **Parallel calls for efficiency** - Tools like get_cs_at_minute, get_stats_at_minute,
   get_hero_positions can be called in parallel for different time points.
"""

# Assemble full instructions from shared constants + server-specific rules
COACHING_INSTRUCTIONS = f"""{COACHING_PERSONA}
{CORE_PHILOSOPHY}
{ANALYSIS_WORKFLOW}
{TOOL_INSTRUCTIONS}"""

mcp = FastMCP(
    name="Dota 2 Match Analysis Server",
    instructions=COACHING_INSTRUCTIONS,
)

# Import resources
# Import prompts
from src.prompts import register_prompts
from src.resources.heroes_resources import heroes_resource
from src.resources.map_resources import get_cached_map_data
from src.resources.pro_scene_resources import pro_scene_resource

# Import services
from src.services.cache.replay_cache import ReplayCache as ReplayCacheV2
from src.services.combat.combat_service import CombatService
from src.services.combat.fight_service import FightService
from src.services.farming.farming_service import FarmingService
from src.services.jungle.jungle_service import JungleService
from src.services.lane.lane_service import LaneService
from src.services.replay.replay_service import ReplayService
from src.services.rotation.rotation_service import RotationService
from src.services.seek.seek_service import SeekService
from src.utils.constants_fetcher import constants_fetcher
from src.utils.match_fetcher import match_fetcher
from src.utils.pro_scene_fetcher import pro_scene_fetcher

# Initialize services
_replay_cache = ReplayCacheV2()
_replay_service = ReplayService(cache=_replay_cache)
_combat_service = CombatService()
_fight_service = FightService(combat_service=_combat_service)
_jungle_service = JungleService()
_lane_service = LaneService()
_seek_service = SeekService()
_farming_service = FarmingService()
_rotation_service = RotationService(combat_service=_combat_service, fight_service=_fight_service)

# Create services dictionary for tool registration
services = {
    "replay_service": _replay_service,
    "combat_service": _combat_service,
    "fight_service": _fight_service,
    "jungle_service": _jungle_service,
    "lane_service": _lane_service,
    "seek_service": _seek_service,
    "farming_service": _farming_service,
    "rotation_service": _rotation_service,
    "heroes_resource": heroes_resource,
    "pro_scene_resource": pro_scene_resource,
    "constants_fetcher": constants_fetcher,
    "match_fetcher": match_fetcher,
    "pro_scene_fetcher": pro_scene_fetcher,
}

# Register all tools from modules
from src.tools import register_all_tools

register_all_tools(mcp, services)

# Register prompts
register_prompts(mcp)


# Define MCP Resources
@mcp.resource(
    "dota2://heroes/all",
    name="All Dota 2 Heroes",
    description="Complete list of all Dota 2 heroes with their canonical names, aliases, and attributes",
    mime_type="application/json"
)
async def all_heroes_resource() -> Dict[str, Dict[str, Any]]:
    """MCP resource that provides all Dota 2 heroes data."""
    return await heroes_resource.get_all_heroes()


@mcp.resource(
    "dota2://map",
    name="Dota 2 Map Data",
    description="Complete Dota 2 map: towers, neutral camps, runes, Roshan, outposts, shops, landmarks",
    mime_type="application/json"
)
async def map_data_resource() -> Dict[str, Any]:
    """MCP resource providing static Dota 2 map data."""
    map_data = get_cached_map_data()
    return map_data.model_dump()


@mcp.resource(
    "dota2://pro/players",
    name="Pro Players",
    description="All professional Dota 2 players with names, teams, and aliases",
    mime_type="application/json"
)
async def pro_players_resource() -> Dict[str, Any]:
    """MCP resource providing all professional players."""
    players = await pro_scene_resource.get_all_players()
    return {"total_players": len(players), "players": players}


@mcp.resource(
    "dota2://pro/teams",
    name="Pro Teams",
    description="All professional Dota 2 teams with ratings and win/loss records",
    mime_type="application/json"
)
async def pro_teams_resource() -> Dict[str, Any]:
    """MCP resource providing all professional teams."""
    teams = await pro_scene_resource.get_all_teams()
    return {"total_teams": len(teams), "teams": teams}


# Diagnostic tool to check client capabilities
from fastmcp import Context


@mcp.tool()
async def get_client_capabilities(ctx: Context) -> Dict[str, Any]:
    """
    Diagnostic tool to check what MCP capabilities the connected client supports.

    Returns information about sampling, roots, and other client capabilities.
    """
    result: Dict[str, Any] = {
        "sampling_supported": False,
        "roots_supported": False,
        "client_info": None,
        "raw_capabilities": None,
    }

    try:
        # Use public ctx.session API (fastmcp 2.13+)
        session = ctx.session
        if session is None:
            result["error"] = "No session available (MCP session not established)"
            result["client_id"] = ctx.client_id
            result["session_id"] = ctx.session_id
            return result

        # Get client params from initialization
        client_params = getattr(session, "_client_params", None)
        if client_params is None:
            client_params = getattr(session, "client_params", None)

        if client_params:
            client_info = getattr(client_params, "clientInfo", None)
            result["client_info"] = {
                "name": getattr(client_info, "name", None) if client_info else None,
                "version": getattr(client_info, "version", None) if client_info else None,
            }

            caps = getattr(client_params, "capabilities", None)
            if caps:
                result["sampling_supported"] = getattr(caps, "sampling", None) is not None
                result["roots_supported"] = getattr(caps, "roots", None) is not None
                result["raw_capabilities"] = str(caps)
        else:
            result["note"] = "Client params not accessible via session"
            result["client_id"] = ctx.client_id
            result["session_id"] = ctx.session_id

    except Exception as e:
        result["error"] = str(e)
        result["client_id"] = ctx.client_id
        result["session_id"] = ctx.session_id

    return result


def main():
    """Main entry point for the server."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Dota 2 Match MCP Server")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8081)), help="Port for SSE")
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.version:
        print("Dota 2 Match MCP Server v1.0.3")
        return

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    if args.debug:
        print("Debug logging enabled", file=sys.stderr)

    print("Dota 2 Match MCP Server starting...", file=sys.stderr)
    print(f"Transport: {args.transport}", file=sys.stderr)

    if args.transport == "sse":
        print(f"Listening on: http://{args.host}:{args.port}", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
