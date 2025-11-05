#!/usr/bin/env python3
"""
Dota 2 Match MCP Server - Match-focused analysis

Provides MCP tools for analyzing specific Dota 2 matches using replay files.
All tools require a match_id and work with actual match data.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add project paths for imports
project_root = Path(__file__).parent.parent
mcp_dir = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(mcp_dir))

from fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("Dota 2 Match Analysis Server")

# Import business logic from resources
from src.resources.heroes_resources import heroes_resource

# Define MCP Resources
@mcp.resource(
    "dota2://heroes/all",
    name="All Dota 2 Heroes",
    description="Complete list of all Dota 2 heroes with their canonical names, aliases, and attributes",
    mime_type="application/json"
)
def all_heroes_resource() -> Dict[str, Dict[str, Any]]:
    """
    MCP resource that provides all Dota 2 heroes data.
    
    Returns:
        Complete heroes data in the same format as heroes.json
    """
    return heroes_resource.get_all_heroes()

@mcp.resource(
    "dota2://heroes/match/{match_id}",
    name="Match Heroes",
    description="Heroes that were picked in a specific Dota 2 match",
    mime_type="application/json"
)
def match_heroes_resource(match_id: str) -> Dict[str, Dict[str, Any]]:
    """
    MCP resource that provides heroes data for a specific match.
    
    Args:
        match_id: The Dota 2 match ID as a string
        
    Returns:
        Heroes data filtered to only include the 10 heroes picked in the match
    """
    try:
        match_id_int = int(match_id)
        return heroes_resource.get_heroes_in_match(match_id_int)
    except ValueError:
        return {"error": f"Invalid match ID: {match_id}"}

# Define MCP Tools
@mcp.tool
def list_match_heroes(match_id: int) -> Dict[str, Any]:
    """
    List the 10 heroes that were picked in a specific Dota 2 match.
    
    Args:
        match_id: The Dota 2 match ID to analyze
        
    Returns:
        Dictionary containing the heroes picked in the match
    """
    heroes = heroes_resource.get_heroes_in_match(match_id)
    if heroes:
        return {
            "success": True,
            "match_id": match_id,
            "hero_count": len(heroes),
            "heroes": heroes
        }
    else:
        return {
            "success": False,
            "match_id": match_id,
            "error": "Could not fetch heroes for this match"
        }


def main():
    """Main entry point for the server."""
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print("Dota 2 Match MCP Server v1.0.0")
        return
    
    # Print server status
    print(f"🎮 Dota 2 Match MCP Server starting with 1 tool...", file=sys.stderr)
    print(f"   list_heroes: ✅", file=sys.stderr)
    
    # Run the server (stdio transport by default)
    mcp.run()


if __name__ == "__main__":
    main()