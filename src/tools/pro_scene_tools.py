"""Pro scene MCP tools: players, teams, leagues, matches."""

from typing import Optional

from ..models.pro_scene import (
    LeagueMatchesResponse,
    LeaguesResponse,
    PlayerSearchResponse,
    ProMatchesResponse,
    ProPlayerResponse,
    TeamMatchesResponse,
    TeamResponse,
    TeamSearchResponse,
    TournamentSeriesResponse,
)


def register_pro_scene_tools(mcp, services):
    """Register pro scene tools with the MCP server."""
    pro_scene_resource = services["pro_scene_resource"]

    @mcp.tool
    async def search_pro_player(query: str, max_results: int = 10) -> PlayerSearchResponse:
        """Search for professional Dota 2 players by name or alias."""
        return await pro_scene_resource.search_player(query, max_results=max_results)

    @mcp.tool
    async def search_team(query: str, max_results: int = 10) -> TeamSearchResponse:
        """Search for professional Dota 2 teams by name, tag, or alias."""
        return await pro_scene_resource.search_team(query, max_results=max_results)

    @mcp.tool
    async def get_pro_player(account_id: int) -> ProPlayerResponse:
        """Get detailed information about a professional player by account ID."""
        return await pro_scene_resource.get_player(account_id)

    @mcp.tool
    async def get_pro_player_by_name(name: str) -> ProPlayerResponse:
        """Get detailed information about a professional player by name."""
        return await pro_scene_resource.get_player_by_name(name)

    @mcp.tool
    async def get_team(team_id: int) -> TeamResponse:
        """Get detailed information about a team by ID."""
        return await pro_scene_resource.get_team(team_id)

    @mcp.tool
    async def get_team_by_name(name: str) -> TeamResponse:
        """Get detailed information about a team by name."""
        return await pro_scene_resource.get_team_by_name(name)

    @mcp.tool
    async def get_team_matches(team_id: int, limit: int = 50) -> TeamMatchesResponse:
        """Get recent matches for a team."""
        return await pro_scene_resource.get_team_matches(team_id, limit=limit)

    @mcp.tool
    async def get_leagues(tier: Optional[str] = None) -> LeaguesResponse:
        """Get all Dota 2 leagues/tournaments."""
        return await pro_scene_resource.get_leagues(tier=tier)

    @mcp.tool
    async def get_pro_matches(
        limit: int = 50,
        tier: Optional[str] = None,
        team1_name: Optional[str] = None,
        team2_name: Optional[str] = None,
        league_name: Optional[str] = None,
        days_back: Optional[int] = None,
    ) -> ProMatchesResponse:
        """Get recent professional Dota 2 matches as a flat list.

        Returns individual matches without series grouping. Use get_tournament_series
        for bracket/series analysis.

        Args:
            limit: Maximum matches to return (default 50)
            tier: Filter by league tier (premium, professional, amateur)
            team1_name: Filter by first team (fuzzy match). Alone: all matches for team.
            team2_name: Filter by second team (fuzzy match). With team1: head-to-head matches.
            league_name: Filter by league/tournament name (contains, case-insensitive)
            days_back: Only return matches from last N days
        """
        return await pro_scene_resource.get_pro_matches(
            limit=limit,
            tier=tier,
            team1_name=team1_name,
            team2_name=team2_name,
            league_name=league_name,
            days_back=days_back,
        )

    @mcp.tool
    async def get_tournament_series(
        league_name: Optional[str] = None,
        league_id: Optional[int] = None,
        team_name: Optional[str] = None,
        limit: int = 20,
        days_back: Optional[int] = None,
    ) -> TournamentSeriesResponse:
        """Get tournament series with bracket/game details.

        Use this for tournament progression analysis: series results, Bo3/Bo5 outcomes,
        team advancement through brackets.

        Args:
            league_name: Filter by league/tournament name (fuzzy match)
            league_id: Filter by specific league ID
            team_name: Filter series involving this team
            limit: Maximum series to return (default 20)
            days_back: Only series from last N days
        """
        return await pro_scene_resource.get_tournament_series(
            league_name=league_name,
            league_id=league_id,
            team_name=team_name,
            limit=limit,
            days_back=days_back,
        )

    @mcp.tool
    async def get_league_matches(league_id: int, limit: int = 100) -> LeagueMatchesResponse:
        """Get matches from a specific league/tournament with series grouping."""
        return await pro_scene_resource.get_league_matches(league_id, limit=limit)
