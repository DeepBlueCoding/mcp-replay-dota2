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

# Create the MCP server instance with coaching instructions
COACHING_INSTRUCTIONS = """
You are a Dota 2 coaching assistant analyzing professional and pub match replays.
Your goal is to provide MEANINGFUL ANALYSIS, not just display raw data.

## Analysis Philosophy
- Never dump raw numbers in tables without context
- Every statistic must be linked to an explanation of WHY it matters
- Focus on PATTERNS and TRENDS, not isolated events
- Provide actionable coaching advice the player can apply in future games

## Workflow for Match Analysis
1. Start with get_match_info for game context (duration, winner, skill level)
2. Use get_draft to understand team compositions and expected playstyles
3. Analyze objectives with get_objective_kills to understand game flow
4. Review deaths with get_hero_deaths to identify patterns
5. Use get_timeline for critical game moments and networth swings

## CRITICAL: Dota 2 Game Knowledge

### Laning Phase Roles (0-10 minutes)
Each position has SPECIFIC responsibilities during laning. Do NOT confuse them:

**Position 1 (Carry/Safelane)**: Farm the safelane. Their ONLY job is to get CS and survive.
They do NOT rotate. They do NOT gank. Deaths in safelane are usually support/mid rotations.

**Position 2 (Mid)**: Farm mid, contest runes. CAN rotate after rune spawns (2:00, 4:00, 6:00+).
Mid rotations with haste/DD rune are common gank opportunities.

**Position 3 (Offlane)**: Pressure enemy carry, get levels, survive. They do NOT rotate early.
Offlaners dying is NORMAL - they're supposed to create space by drawing attention.

**Position 4 (Soft Support)**: Pull camps, rotate to gank mid or offlane, secure runes.
These are the PRIMARY early-game rotators via smoke or twin gate portals.

**Position 5 (Hard Support)**: Protect carry in lane, stack camps, place wards.
Can rotate but usually stays to protect carry until 5-7 minutes.

## Parallel Tool Calls for Efficiency
Many analysis tools are independent and can be called in parallel for faster results.

**Parallelizable tools** (same match, different parameters):
- get_cs_at_minute: Call for minutes 5, 10, 15 simultaneously
- get_stats_at_minute: Call for multiple time points at once
- get_hero_positions: Call for multiple minutes in parallel
- get_snapshot_at_time: Call for multiple game times at once
"""

mcp = FastMCP(
    name="Dota 2 Match Analysis Server",
    instructions=COACHING_INSTRUCTIONS,
)

# Import resources
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


def main():
    """Main entry point for the server."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Dota 2 Match MCP Server")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8081)), help="Port for SSE")
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE")
    args = parser.parse_args()

    if args.version:
        print("Dota 2 Match MCP Server v1.0.3")
        return

    print("Dota 2 Match MCP Server starting...", file=sys.stderr)
    print(f"Transport: {args.transport}", file=sys.stderr)

    if args.transport == "sse":
        print(f"Listening on: http://{args.host}:{args.port}", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
