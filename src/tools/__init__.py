"""MCP Tools organized by domain."""

from .analysis_tools import register_analysis_tools
from .combat_tools import register_combat_tools
from .fight_tools import register_fight_tools
from .match_tools import register_match_tools
from .pro_scene_tools import register_pro_scene_tools
from .replay_tools import register_replay_tools


def register_all_tools(mcp, services):
    """Register all tools with the MCP server."""
    register_replay_tools(mcp, services)
    register_combat_tools(mcp, services)
    register_fight_tools(mcp, services)
    register_match_tools(mcp, services)
    register_pro_scene_tools(mcp, services)
    register_analysis_tools(mcp, services)
