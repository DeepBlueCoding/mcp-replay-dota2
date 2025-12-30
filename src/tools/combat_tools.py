"""Combat-related MCP tools: deaths, combat log, objectives, items, couriers, runes."""

from typing import Literal, Optional

from fastmcp import Context

from ..coaching import (
    get_death_analysis_prompt,
    get_hero_performance_prompt,
    try_coaching_analysis,
)
from ..models.combat_log import (
    CombatLogResponse,
    CourierKillsResponse,
    DetailLevel,
    HeroCombatAnalysisResponse,
    HeroDeathsResponse,
    ItemPurchasesResponse,
    ObjectiveKillsResponse,
    RunePickupsResponse,
)
from ..models.filters import DeathFilters, HeroPerformanceFilters
from ..models.game_context import GameContext


def register_combat_tools(mcp, services):
    """Register combat-related tools with the MCP server."""
    replay_service = services["replay_service"]
    combat_service = services["combat_service"]

    @mcp.tool
    async def get_hero_deaths(
        match_id: int,
        killer: Optional[str] = None,
        victim: Optional[str] = None,
        location: Optional[str] = None,
        ability: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        ctx: Optional[Context] = None,
    ) -> HeroDeathsResponse:
        """
        Get chronological list of ALL hero deaths in a match.

        Returns all deaths with killer, victim, time, location, and ability used.
        Use for global death timeline, first blood, or death pattern analysis.

        Args:
            match_id: The Dota 2 match ID
            killer: Filter by killer hero (partial match, e.g. 'jugg')
            victim: Filter by victim hero (partial match)
            location: Filter by map location (partial match, e.g. 't1', 'roshan')
            ability: Filter by killing ability (partial match)
            start_time: Filter deaths after this game time (seconds)
            end_time: Filter deaths before this game time (seconds)
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            game_context = GameContext.from_parsed_data(data)
            response = combat_service.get_hero_deaths_response(
                data, match_id, game_context=game_context
            )

            # Apply filters
            filters = DeathFilters.from_params(
                killer=killer,
                victim=victim,
                location=location,
                ability=ability,
                start_time=start_time,
                end_time=end_time,
            )
            response.deaths = filters.apply(response.deaths)
            response.total_deaths = len(response.deaths)

            if response.success and len(response.deaths) >= 3:
                hero_positions = {}
                for death in response.deaths:
                    victim_name = death.victim.lower()
                    if victim_name not in hero_positions:
                        hero_positions[victim_name] = "?"

                deaths_data = [
                    {
                        "victim": d.victim,
                        "killer": d.killer,
                        "game_time": d.game_time,
                        "ability": d.ability,
                    }
                    for d in response.deaths
                ]
                prompt = get_death_analysis_prompt(deaths_data, hero_positions)
                coaching = await try_coaching_analysis(ctx, prompt, max_tokens=700)
                response.coaching_analysis = coaching

            return response
        except ValueError as e:
            return HeroDeathsResponse(success=False, match_id=match_id, error=str(e))

    @mcp.tool
    async def get_raw_combat_events(
        match_id: int,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        hero_filter: Optional[str] = None,
        ability_filter: Optional[str] = None,
        detail_level: Literal["narrative", "tactical", "full"] = "narrative",
        max_events: int = 200,
        ctx: Optional[Context] = None,
    ) -> CombatLogResponse:
        """
        Get raw combat events for a specific time window.

        Use for analyzing non-fight moments (e.g., Roshan attempts, specific plays).
        detail_level: "narrative" (deaths/abilities), "tactical" (+damage), "full" (all).

        Args:
            match_id: The Dota 2 match ID
            start_time: Start of time window in seconds
            end_time: End of time window in seconds
            hero_filter: Filter to specific hero
            ability_filter: Filter to specific ability
            detail_level: "narrative", "tactical", or "full"
            max_events: Maximum events to return
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            level = DetailLevel(detail_level)
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            return combat_service.get_combat_log_response(
                data, match_id, start_time, end_time, hero_filter,
                ability_filter=ability_filter,
                detail_level=level,
                max_events=max_events,
            )
        except ValueError as e:
            return CombatLogResponse(success=False, match_id=match_id, error=str(e))

    @mcp.tool
    async def get_item_purchases(
        match_id: int,
        hero_filter: Optional[str] = None,
        ctx: Optional[Context] = None,
    ) -> ItemPurchasesResponse:
        """
        Get item purchase timings for heroes in a Dota 2 match.

        Returns a chronological list of item purchases with:
        - game_time: Seconds since game start (can be negative for pre-horn purchases)
        - game_time_str: Formatted as M:SS
        - hero: Hero that purchased the item
        - item: Item name (e.g., "item_bfury", "item_power_treads")

        Use this to answer questions like:
        - "When did Juggernaut finish Battlefury?"
        - "What was Anti-Mage's item progression?"
        - "Who bought the first BKB?"

        Args:
            match_id: The Dota 2 match ID
            hero_filter: Only include purchases by this hero, e.g. "juggernaut" (optional)

        Returns:
            ItemPurchasesResponse with list of item purchase events
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            return combat_service.get_item_purchases_response(data, match_id, hero_filter)
        except ValueError as e:
            return ItemPurchasesResponse(success=False, match_id=match_id, error=str(e))

    @mcp.tool
    async def get_courier_kills(
        match_id: int,
        ctx: Optional[Context] = None,
    ) -> CourierKillsResponse:
        """
        Get all courier kills in a Dota 2 match.

        Returns a list of courier kill events with:
        - game_time: Seconds since game start
        - game_time_str: Formatted as M:SS
        - killer: Hero that killed the courier
        - killer_is_hero: Whether the killer was a hero
        - team: Team whose courier was killed (radiant/dire)

        Args:
            match_id: The Dota 2 match ID

        Returns:
            CourierKillsResponse with list of courier kill events
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            game_context = GameContext.from_parsed_data(data)
            return combat_service.get_courier_kills_response(
                data, match_id, game_context=game_context
            )
        except ValueError as e:
            return CourierKillsResponse(success=False, match_id=match_id, error=str(e))

    @mcp.tool
    async def get_objective_kills(
        match_id: int,
        ctx: Optional[Context] = None,
    ) -> ObjectiveKillsResponse:
        """
        Get all major objective kills in a Dota 2 match.

        Returns kills of:
        - Roshan: game_time, killer, team, kill_number (1st, 2nd, 3rd Roshan)
        - Tormentor: game_time, killer, team, side (which Tormentor was killed)
        - Towers: game_time, tower name, team, tier, lane, killer
        - Barracks: game_time, barracks name, team, lane, type (melee/ranged), killer

        Use this to analyze:
        - When did each team take Roshan?
        - Tower trade patterns and timing
        - High ground pushes and barracks destruction
        - Tormentor control

        Args:
            match_id: The Dota 2 match ID

        Returns:
            ObjectiveKillsResponse with all objective kill events
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            return combat_service.get_objective_kills_response(data, match_id)
        except ValueError as e:
            return ObjectiveKillsResponse(success=False, match_id=match_id, error=str(e))

    @mcp.tool
    async def get_rune_pickups(match_id: int, ctx: Optional[Context] = None) -> RunePickupsResponse:
        """
        Get power rune pickups in a Dota 2 match.

        Returns a list of power rune pickup events with:
        - game_time: Seconds since game start
        - game_time_str: Formatted as M:SS
        - hero: Hero that picked up the rune
        - rune_type: Type of rune (haste, double_damage, arcane, invisibility, regeneration, shield)

        Note: Only power runes are trackable. Bounty, wisdom, and water runes
        don't leave detectable events in the replay data.

        Use this to answer questions like:
        - "Who got the most power runes?"
        - "What runes did the mid player secure?"
        - "When did they get a DD rune before fighting?"

        Args:
            match_id: The Dota 2 match ID

        Returns:
            RunePickupsResponse with list of power rune pickup events
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            return combat_service.get_rune_pickups_response(data, match_id)
        except ValueError as e:
            return RunePickupsResponse(success=False, match_id=match_id, error=str(e))

    fight_service = services["fight_service"]

    @mcp.tool
    async def get_hero_performance(
        match_id: int,
        hero: str,
        ability_filter: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        ctx: Optional[Context] = None,
    ) -> HeroCombatAnalysisResponse:
        """
        Get comprehensive performance data for a hero.

        Returns kills, deaths, assists, ability stats (casts, hit rate), and
        per-fight breakdowns. Use ability_filter for specific ability analysis.

        Time filtering: Use start_time/end_time to analyze specific game phases.
        Common time ranges:
        - Early game: start_time=0, end_time=900 (0-15 min)
        - Mid game: start_time=900, end_time=1800 (15-30 min)
        - Late game: start_time=1800 (30+ min)

        Args:
            match_id: The Dota 2 match ID
            hero: Hero name (e.g., "jakiro", "mars", "batrider")
            ability_filter: Filter to specific ability (e.g., "ice_path", "flaming_lasso")
            start_time: Filter fights starting after this game time (seconds)
            end_time: Filter fights starting before this game time (seconds)
        """
        from ..utils.match_fetcher import match_fetcher

        async def progress_callback(current: int, total: int, message: str) -> None:
            if ctx:
                await ctx.report_progress(current, total)

        try:
            data = await replay_service.get_parsed_data(match_id, progress=progress_callback)
            fight_result = fight_service.get_all_fights(data)
            response = combat_service.get_hero_combat_analysis(
                data, match_id, hero, fight_result.fights,
                ability_filter=ability_filter,
            )

            # Apply time filters if specified
            filters = HeroPerformanceFilters.from_params(
                ability=ability_filter,
                start_time=start_time,
                end_time=end_time,
            )
            if not filters.is_empty() and response.success:
                filtered_fights = filters.apply_to_fights(response.fights)
                response.fights = filtered_fights
                totals = filters.recalculate_totals(filtered_fights)
                response.total_kills = totals["total_kills"]
                response.total_deaths = totals["total_deaths"]
                response.total_assists = totals["total_assists"]
                response.total_teamfights = totals["total_teamfights"]
                response.total_fights = totals["total_fights"]
                response.ability_summary = filters.recalculate_ability_summary(filtered_fights)

            if response.success:
                position = None
                try:
                    match_data = await match_fetcher.get_match(match_id)
                    if match_data and "players" in match_data:
                        from ..utils.constants_fetcher import constants_fetcher
                        from ..utils.match_fetcher import assign_positions
                        players = match_data["players"]
                        assign_positions(players)
                        hero_lower = hero.lower()
                        for p in players:
                            hero_id = p.get("hero_id")
                            if hero_id:
                                hero_name = constants_fetcher.get_hero_name(hero_id)
                                if hero_name and hero_lower in hero_name.lower():
                                    position = p.get("position")
                                    break
                except Exception:
                    pass

                response.position = position

                ability_stats = "N/A"
                if response.ability_summary:
                    ability_stats = ", ".join([
                        f"{a.ability}: {a.total_casts} casts ({a.hit_rate:.0f}% hit)"
                        for a in response.ability_summary[:5]
                    ])

                raw_data = {
                    "kills": response.total_kills,
                    "deaths": response.total_deaths,
                    "assists": response.total_assists,
                    "fights_participated": response.total_fights,
                    "total_fights": response.total_fights + response.total_teamfights,
                    "ability_stats": ability_stats,
                }

                if position:
                    prompt = get_hero_performance_prompt(hero, position, raw_data)
                    coaching = await try_coaching_analysis(ctx, prompt, max_tokens=700)
                    response.coaching_analysis = coaching

            return response
        except ValueError as e:
            return HeroCombatAnalysisResponse(
                success=False, match_id=match_id, hero=hero, error=str(e)
            )
