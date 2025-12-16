"""Pydantic response models for MCP tools.

These models provide proper output schemas for FastMCP's automatic
structuredContent generation.
"""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from src.models.match_info import DraftResult, MatchInfoResult
from src.models.types import CoercedInt, CoercedIntList

# =============================================================================
# Match Timeline Tools
# =============================================================================


class KDASnapshot(BaseModel):
    """KDA snapshot at a specific game time."""

    game_time: float = Field(description="Game time in seconds")
    kills: CoercedInt = Field(description="Kills at this time")
    deaths: CoercedInt = Field(description="Deaths at this time")
    assists: CoercedInt = Field(description="Assists at this time")
    level: CoercedInt = Field(description="Hero level at this time")


class PlayerTimeline(BaseModel):
    """Timeline data for a single player."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Player's team")
    net_worth: CoercedIntList = Field(description="Net worth values (sampled every 30 seconds)")
    hero_damage: CoercedIntList = Field(description="Cumulative hero damage values")
    kda_timeline: List[KDASnapshot] = Field(description="KDA snapshots over time")


class TeamGraphs(BaseModel):
    """Team-level timeline graphs."""

    radiant_xp: CoercedIntList = Field(description="Radiant team XP over time")
    dire_xp: CoercedIntList = Field(description="Dire team XP over time")
    radiant_gold: CoercedIntList = Field(description="Radiant team gold over time")
    dire_gold: CoercedIntList = Field(description="Dire team gold over time")


class MatchTimelineResponse(BaseModel):
    """Response for get_match_timeline tool."""

    success: bool
    match_id: Optional[int] = None
    players: List[PlayerTimeline] = Field(default_factory=list)
    team_graphs: Optional[TeamGraphs] = None
    error: Optional[str] = None


class PlayerStatsAtMinute(BaseModel):
    """Player stats at a specific game minute."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Player's team")
    net_worth: CoercedInt = Field(description="Net worth at this minute")
    hero_damage: CoercedInt = Field(description="Cumulative hero damage")
    kills: CoercedInt = Field(description="Kills")
    deaths: CoercedInt = Field(description="Deaths")
    assists: CoercedInt = Field(description="Assists")
    level: CoercedInt = Field(description="Hero level")


class StatsAtMinuteResponse(BaseModel):
    """Response for get_stats_at_minute tool."""

    success: bool
    match_id: int
    minute: int = Field(default=0, description="The minute these stats are for")
    players: List[PlayerStatsAtMinute] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# Match Info Tools
# =============================================================================


class MatchDraftResponse(BaseModel):
    """Response for get_match_draft tool."""

    success: bool
    match_id: int
    draft: Optional[DraftResult] = Field(default=None, description="Complete draft information")
    error: Optional[str] = None


class MatchInfoResponse(BaseModel):
    """Response for get_match_info tool."""

    success: bool
    match_id: int
    info: Optional[MatchInfoResult] = Field(default=None, description="Match info including teams and players")
    error: Optional[str] = None


class HeroStats(BaseModel):
    """Detailed hero statistics from a match."""

    hero_id: CoercedInt = Field(description="Hero ID")
    hero_name: str = Field(description="Hero internal name")
    localized_name: str = Field(description="Hero display name")
    team: Literal["radiant", "dire"] = Field(description="Team")
    player_name: Optional[str] = Field(default=None, description="Player name")
    pro_name: Optional[str] = Field(default=None, description="Pro player name if known")
    position: Optional[CoercedInt] = Field(default=None, description="Position 1-5")
    rank_tier: Optional[CoercedInt] = Field(default=None, description="Player rank tier")
    kills: CoercedInt = Field(description="Kills")
    deaths: CoercedInt = Field(description="Deaths")
    assists: CoercedInt = Field(description="Assists")
    last_hits: CoercedInt = Field(description="Last hits")
    denies: CoercedInt = Field(description="Denies")
    gpm: CoercedInt = Field(description="Gold per minute")
    xpm: CoercedInt = Field(description="XP per minute")
    net_worth: CoercedInt = Field(description="Final net worth")
    hero_damage: CoercedInt = Field(description="Total hero damage")
    tower_damage: CoercedInt = Field(description="Total tower damage")
    hero_healing: CoercedInt = Field(description="Total hero healing")
    teamfight_participation: Optional[float] = Field(default=None, description="Teamfight participation %")
    stuns: Optional[float] = Field(default=None, description="Total stun duration dealt in seconds")
    camps_stacked: Optional[CoercedInt] = Field(default=None, description="Neutral camps stacked")
    obs_placed: Optional[CoercedInt] = Field(default=None, description="Observer wards placed")
    sen_placed: Optional[CoercedInt] = Field(default=None, description="Sentry wards placed")
    lane: Optional[str] = Field(default=None, description="Lane assignment")
    lane_efficiency: Optional[float] = Field(default=None, description="Lane efficiency (0.0-1.0)")
    role: Optional[str] = Field(default=None, description="Role (core/support)")
    items: List[str] = Field(default_factory=list, description="Final items")
    item_neutral: Optional[str] = Field(default=None, description="Neutral item")
    item_neutral2: Optional[str] = Field(default=None, description="Second neutral item (7.40+)")


class MatchHeroesResponse(BaseModel):
    """Response for get_match_heroes tool."""

    success: bool
    match_id: int
    radiant_heroes: List[HeroStats] = Field(default_factory=list)
    dire_heroes: List[HeroStats] = Field(default_factory=list)
    error: Optional[str] = None


class MatchPlayerInfo(BaseModel):
    """Player info for get_match_players."""

    player_name: str = Field(description="Steam display name")
    pro_name: Optional[str] = Field(default=None, description="Pro player name if known")
    account_id: Optional[int] = Field(default=None, description="Steam account ID")
    rank_tier: Optional[int] = Field(default=None, description="Player rank tier (e.g., 85=Divine 5, 80+=Immortal)")
    hero_id: int = Field(description="Hero ID")
    hero_name: str = Field(description="Hero internal name")
    localized_name: str = Field(description="Hero display name")
    position: Optional[int] = Field(default=None, description="Position 1-5")


class MatchPlayersResponse(BaseModel):
    """Response for get_match_players tool."""

    success: bool
    match_id: int
    radiant: List[MatchPlayerInfo] = Field(default_factory=list)
    dire: List[MatchPlayerInfo] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# Fight Tools
# =============================================================================


class FightDeath(BaseModel):
    """A death within a fight."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time as M:SS")
    killer: str = Field(description="Hero that got the kill")
    killer_level: Optional[int] = Field(default=None, description="Killer's hero level")
    victim: str = Field(description="Hero that died")
    victim_level: Optional[int] = Field(default=None, description="Victim's hero level")
    level_advantage: Optional[int] = Field(default=None, description="Killer's level advantage")
    ability: Optional[str] = Field(default=None, description="Killing ability")


class FightSummary(BaseModel):
    """Summary of a fight."""

    fight_id: str = Field(description="Unique fight identifier")
    start_time: float = Field(description="Start time in seconds")
    start_time_str: str = Field(description="Start time as M:SS")
    end_time: float = Field(description="End time in seconds")
    end_time_str: str = Field(description="End time as M:SS")
    duration_seconds: float = Field(description="Fight duration")
    total_deaths: int = Field(description="Number of deaths in fight")
    is_teamfight: bool = Field(description="True if 3+ deaths")
    participants: List[str] = Field(default_factory=list, description="Heroes involved")
    deaths: List[FightDeath] = Field(default_factory=list, description="Deaths in the fight")


class FightListResponse(BaseModel):
    """Response for list_fights tool."""

    success: bool
    match_id: int
    total_fights: int = Field(default=0, description="Number of distinct fights")
    teamfights: int = Field(default=0, description="Number of teamfights (3+ deaths)")
    skirmishes: int = Field(default=0, description="Number of skirmishes (1-2 deaths)")
    total_deaths: int = Field(default=0, description="Total hero deaths")
    fights: List[FightSummary] = Field(default_factory=list)
    error: Optional[str] = None


class TeamfightsResponse(BaseModel):
    """Response for get_teamfights tool."""

    success: bool
    match_id: int
    min_deaths_threshold: int = Field(default=3, description="Minimum deaths to classify as teamfight")
    total_teamfights: int = Field(default=0)
    teamfights: List[FightSummary] = Field(default_factory=list)
    coaching_analysis: Optional[str] = Field(
        default=None,
        description="AI coaching analysis of teamfights (requires sampling-capable client)"
    )
    error: Optional[str] = None


class FightDeathDetail(BaseModel):
    """Detailed death info for get_fight."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time as M:SS")
    killer: str = Field(description="Hero that got the kill")
    killer_is_hero: bool = Field(description="Whether killer was a hero")
    killer_level: Optional[int] = Field(default=None, description="Killer's hero level")
    victim: str = Field(description="Hero that died")
    victim_level: Optional[int] = Field(default=None, description="Victim's hero level")
    level_advantage: Optional[int] = Field(default=None, description="Killer's level advantage")
    ability: Optional[str] = Field(default=None, description="Killing ability")
    position_x: Optional[float] = Field(default=None, description="X coordinate")
    position_y: Optional[float] = Field(default=None, description="Y coordinate")


class FightDetailResponse(BaseModel):
    """Response for get_fight tool."""

    success: bool
    match_id: int
    fight_id: str = Field(default="", description="Fight identifier")
    start_time: float = Field(default=0.0)
    start_time_str: str = Field(default="0:00")
    start_time_seconds: float = Field(default=0.0)
    end_time: float = Field(default=0.0)
    end_time_str: str = Field(default="0:00")
    end_time_seconds: float = Field(default=0.0)
    duration_seconds: float = Field(default=0.0)
    is_teamfight: bool = Field(default=False)
    total_deaths: int = Field(default=0)
    participants: List[str] = Field(default_factory=list)
    deaths: List[FightDeathDetail] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# Jungle and Lane Analysis Tools
# =============================================================================


class CampStack(BaseModel):
    """A camp stack event."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time as M:SS")
    stacker: str = Field(description="Hero that stacked the camp")
    camp_type: Optional[str] = Field(default=None, description="Camp type (ancient/large/medium/small)")
    stack_count: int = Field(description="Number of creeps in stack")


class CampStacksResponse(BaseModel):
    """Response for get_camp_stacks tool."""

    success: bool
    match_id: int
    hero_filter: Optional[str] = Field(default=None, description="Hero filter applied")
    total_stacks: int = Field(default=0)
    stacks: List[CampStack] = Field(default_factory=list)
    error: Optional[str] = None


class JungleSummaryResponse(BaseModel):
    """Response for get_jungle_summary tool."""

    success: bool
    match_id: int
    total_stacks: int = Field(default=0)
    stacks_by_hero: Dict[str, int] = Field(default_factory=dict, description="Stack count per hero")
    stack_efficiency_per_10min: Dict[str, float] = Field(
        default_factory=dict, description="Stacks per 10 minutes per hero"
    )
    error: Optional[str] = None


class LaneWinners(BaseModel):
    """Lane winners summary."""

    top: str = Field(description="Top lane winner (radiant/dire/even)")
    mid: str = Field(description="Mid lane winner (radiant/dire/even)")
    bot: str = Field(description="Bot lane winner (radiant/dire/even)")


class TeamScores(BaseModel):
    """Team laning scores."""

    radiant: float = Field(description="Radiant laning score")
    dire: float = Field(description="Dire laning score")


class HeroLaneStats(BaseModel):
    """Per-hero laning statistics."""

    hero: str = Field(description="Hero name")
    lane: Optional[str] = Field(default=None, description="Lane (top/mid/bot)")
    role: Optional[str] = Field(default=None, description="Role")
    team: Literal["radiant", "dire"] = Field(description="Team")
    last_hits_5min: CoercedInt = Field(default=0, description="Last hits at 5 minutes")
    last_hits_10min: CoercedInt = Field(default=0, description="Last hits at 10 minutes")
    denies_5min: CoercedInt = Field(default=0, description="Denies at 5 minutes")
    denies_10min: CoercedInt = Field(default=0, description="Denies at 10 minutes")
    gold_5min: CoercedInt = Field(default=0, description="Gold at 5 minutes")
    gold_10min: CoercedInt = Field(default=0, description="Gold at 10 minutes")
    level_5min: CoercedInt = Field(default=0, description="Level at 5 minutes")
    level_10min: CoercedInt = Field(default=0, description="Level at 10 minutes")
    lane_efficiency: Optional[float] = Field(default=None, description="Lane efficiency (0.0-1.0)")


class LaneSummaryResponse(BaseModel):
    """Response for get_lane_summary tool."""

    success: bool
    match_id: int
    lane_winners: Optional[LaneWinners] = None
    team_scores: Optional[TeamScores] = None
    hero_stats: List[HeroLaneStats] = Field(default_factory=list)
    coaching_analysis: Optional[str] = Field(
        default=None,
        description="AI coaching analysis of laning phase (requires sampling-capable client)"
    )
    error: Optional[str] = None


class HeroCSData(BaseModel):
    """CS data for a hero at a specific minute."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Team")
    last_hits: CoercedInt = Field(description="Last hits")
    denies: CoercedInt = Field(description="Denies")
    gold: CoercedInt = Field(description="Net worth")
    level: CoercedInt = Field(description="Hero level")


class CSAtMinuteResponse(BaseModel):
    """Response for get_cs_at_minute tool."""

    success: bool
    match_id: int
    minute: int = Field(default=0, description="Game minute")
    heroes: List[HeroCSData] = Field(default_factory=list)
    error: Optional[str] = None


class HeroPosition(BaseModel):
    """Hero position at a specific time."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Team")
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    game_time: float = Field(description="Game time in seconds")


class HeroPositionsResponse(BaseModel):
    """Response for get_hero_positions tool."""

    success: bool
    match_id: int
    minute: int = Field(default=0, description="Game minute")
    positions: List[HeroPosition] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# Game State Tools
# =============================================================================


class HeroSnapshot(BaseModel):
    """Hero state at a specific moment."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Team")
    player_id: CoercedInt = Field(description="Player slot ID")
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    health: CoercedInt = Field(description="Current health")
    max_health: CoercedInt = Field(description="Maximum health")
    mana: CoercedInt = Field(description="Current mana")
    max_mana: CoercedInt = Field(description="Maximum mana")
    level: CoercedInt = Field(description="Hero level")
    alive: bool = Field(description="Whether hero is alive")


class SnapshotAtTimeResponse(BaseModel):
    """Response for get_snapshot_at_time tool."""

    success: bool
    match_id: int
    tick: CoercedInt = Field(default=0, description="Game tick")
    game_time: float = Field(default=0.0, description="Game time in seconds")
    game_time_str: str = Field(default="0:00", description="Game time as M:SS")
    radiant_gold: CoercedInt = Field(default=0, description="Radiant total gold")
    dire_gold: CoercedInt = Field(default=0, description="Dire total gold")
    heroes: List[HeroSnapshot] = Field(default_factory=list)
    error: Optional[str] = None


class PositionPoint(BaseModel):
    """A position at a specific tick."""

    tick: CoercedInt = Field(description="Game tick")
    game_time: float = Field(description="Game time in seconds")
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")


class HeroPositionTimeline(BaseModel):
    """Position timeline for a single hero."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Team")
    positions: List[PositionPoint] = Field(default_factory=list)


class PositionTimelineResponse(BaseModel):
    """Response for get_position_timeline tool."""

    success: bool
    match_id: int
    start_time: float = Field(default=0.0)
    end_time: float = Field(default=0.0)
    interval_seconds: float = Field(default=1.0)
    hero_filter: Optional[str] = None
    heroes: List[HeroPositionTimeline] = Field(default_factory=list)
    error: Optional[str] = None


class FightSnapshotHero(BaseModel):
    """Hero state in a fight snapshot."""

    hero: str = Field(description="Hero name")
    team: Literal["radiant", "dire"] = Field(description="Team")
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    health: CoercedInt = Field(description="Current health")
    max_health: CoercedInt = Field(description="Maximum health")
    alive: bool = Field(description="Whether hero is alive")


class FightSnapshot(BaseModel):
    """A snapshot during a fight."""

    tick: CoercedInt = Field(description="Game tick")
    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time as M:SS")
    heroes: List[FightSnapshotHero] = Field(default_factory=list)


class FightReplayResponse(BaseModel):
    """Response for get_fight_replay tool."""

    success: bool
    match_id: int
    start_tick: CoercedInt = Field(default=0)
    end_tick: CoercedInt = Field(default=0)
    start_time: float = Field(default=0.0)
    start_time_str: str = Field(default="0:00")
    end_time: float = Field(default=0.0)
    end_time_str: str = Field(default="0:00")
    interval_seconds: float = Field(default=0.5)
    total_snapshots: CoercedInt = Field(default=0)
    snapshots: List[FightSnapshot] = Field(default_factory=list)
    error: Optional[str] = None
