"""
Data models for lane analysis.

Provides detailed laning phase tracking: last hits, denies, harass, tower proximity,
rotations (smoke/TP/twin gate), and wave nuking.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.types import CoercedInt


class LaneLastHit(BaseModel):
    """A single last hit or deny event in lane."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    hero: str = Field(description="Hero that got the last hit")
    target: str = Field(description="Creep that was killed")
    is_deny: bool = Field(default=False, description="True if this was a deny")
    position_x: Optional[float] = Field(default=None, description="X coordinate")
    position_y: Optional[float] = Field(default=None, description="Y coordinate")
    lane: str = Field(description="Lane where CS occurred: top, mid, bot, or jungle")
    wave_number: Optional[int] = Field(default=None, description="Wave number (1=first wave)")


class CreepWave(BaseModel):
    """A single creep wave with all deaths tracked."""

    wave_number: int = Field(description="Wave number (1=first wave, spawns at 0:00)")
    spawn_time: float = Field(description="Time wave spawned (0, 30, 60, ...)")
    spawn_time_str: str = Field(description="Spawn time formatted as M:SS")
    first_death_time: Optional[float] = Field(default=None, description="Time of first creep death")
    last_death_time: Optional[float] = Field(default=None, description="Time of last creep death")
    lane: str = Field(description="Lane: top, mid, bot")
    team: str = Field(description="Team whose creeps: radiant or dire")
    melee_deaths: int = Field(default=0, description="Melee creeps killed (max 3)")
    ranged_deaths: int = Field(default=0, description="Ranged creeps killed (max 1)")
    total_deaths: int = Field(default=0, description="Total creeps killed")
    last_hits: List["LaneLastHit"] = Field(default_factory=list, description="All CS from this wave")


class LaneHarass(BaseModel):
    """A harass/trade event between heroes in lane."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    attacker: str = Field(description="Hero dealing damage")
    target: str = Field(description="Hero receiving damage")
    damage: CoercedInt = Field(description="Damage dealt")
    ability: Optional[str] = Field(default=None, description="Ability used (None = right-click)")
    lane: str = Field(description="Lane where harass occurred")


class TowerProximityEvent(BaseModel):
    """Event when a hero enters/leaves tower range (via modifier_tower_aura_bonus)."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    hero: str = Field(description="Hero near the tower")
    tower_team: str = Field(description="Team owning the tower: radiant or dire")
    event_type: str = Field(description="'entered' or 'left' tower range")


class WaveNuke(BaseModel):
    """Detection of a hero using AoE ability on lane creeps (wave pushing)."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    hero: str = Field(description="Hero casting the ability")
    ability: str = Field(description="Ability used to nuke the wave")
    creeps_hit: CoercedInt = Field(description="Number of creeps damaged")
    total_damage: CoercedInt = Field(description="Total damage dealt to creeps")
    lane: str = Field(description="Lane where wave nuke occurred")


class LaneRotation(BaseModel):
    """A rotation event detected in lane (smoke, TP, twin gate)."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    hero: str = Field(description="Hero performing the rotation")
    rotation_type: str = Field(description="smoke_break, tp_scroll, twin_gate")
    from_position_x: Optional[float] = Field(default=None, description="Starting X coordinate")
    from_position_y: Optional[float] = Field(default=None, description="Starting Y coordinate")
    to_lane: Optional[str] = Field(default=None, description="Target lane if detectable")


class NeutralAggro(BaseModel):
    """Hero attacking neutral creeps (pull attempts, aggro manipulation)."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    hero: str = Field(description="Hero attacking neutrals")
    target: str = Field(description="Neutral creep targeted")
    damage: CoercedInt = Field(default=0, description="Damage dealt (0 for attack events)")
    camp_type: Optional[str] = Field(default=None, description="Camp tier: small, medium, large, ancient")
    position_x: Optional[float] = Field(default=None, description="X coordinate")
    position_y: Optional[float] = Field(default=None, description="Y coordinate")
    near_lane: Optional[str] = Field(default=None, description="Nearest lane (for pull detection)")


class TowerPressure(BaseModel):
    """Tower attacking a hero (tower pressure/aggro events)."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    tower: str = Field(description="Tower name (e.g., goodguys_tower1_top)")
    hero: str = Field(description="Hero being attacked by tower")
    damage: CoercedInt = Field(description="Damage dealt by tower")
    tower_team: str = Field(description="Tower team: radiant or dire")
    lane: str = Field(description="Lane of the tower: top, mid, bot")


class HeroLanePhase(BaseModel):
    """Comprehensive laning phase stats for a single hero."""

    hero: str = Field(description="Hero name")
    team: str = Field(description="radiant or dire")
    lane: str = Field(description="Assigned lane: top, mid, bot")
    role: str = Field(description="Role: core, support, mid")

    last_hits_5min: CoercedInt = Field(default=0, description="Last hits at 5:00")
    last_hits_10min: CoercedInt = Field(default=0, description="Last hits at 10:00")
    denies_5min: CoercedInt = Field(default=0, description="Denies at 5:00")
    denies_10min: CoercedInt = Field(default=0, description="Denies at 10:00")

    gold_5min: CoercedInt = Field(default=0, description="Net worth at 5:00")
    gold_10min: CoercedInt = Field(default=0, description="Net worth at 10:00")
    level_5min: CoercedInt = Field(default=1, description="Level at 5:00")
    level_10min: CoercedInt = Field(default=1, description="Level at 10:00")

    damage_dealt_to_heroes: CoercedInt = Field(default=0, description="Total harass damage dealt")
    damage_received_from_heroes: CoercedInt = Field(default=0, description="Total harass damage received")

    time_under_enemy_tower: float = Field(default=0.0, description="Seconds under enemy tower")
    time_under_own_tower: float = Field(default=0.0, description="Seconds under own tower")

    # Neutral aggro (pulls, aggro manipulation)
    neutral_attacks: CoercedInt = Field(default=0, description="Number of attacks on neutral creeps")
    pull_attempts: CoercedInt = Field(default=0, description="Estimated pull attempts (neutral aggro near lane)")

    # Tower pressure
    tower_damage_taken: CoercedInt = Field(default=0, description="Total damage taken from enemy towers")
    tower_hits_received: CoercedInt = Field(default=0, description="Number of tower hits received")

    last_hit_events: List[LaneLastHit] = Field(default_factory=list, description="All CS events")
    harass_events: List[LaneHarass] = Field(default_factory=list, description="All harass events")
    neutral_aggro_events: List["NeutralAggro"] = Field(default_factory=list, description="Neutral aggro events")
    tower_pressure_events: List["TowerPressure"] = Field(default_factory=list, description="Tower damage events")


class HeroPosition(BaseModel):
    """Hero position at a specific time."""

    game_time: float = Field(description="Game time in seconds")
    tick: int = Field(description="Replay tick")
    hero: str = Field(description="Hero name")
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    team: str = Field(description="radiant or dire")


class LaneSummaryResponse(BaseModel):
    """Complete laning phase summary response."""

    success: bool = Field(default=True)
    match_id: int = Field(description="Match ID")

    top_winner: Optional[str] = Field(default=None, description="Top lane winner: radiant, dire, or even")
    mid_winner: Optional[str] = Field(default=None, description="Mid lane winner")
    bot_winner: Optional[str] = Field(default=None, description="Bot lane winner")

    radiant_laning_score: float = Field(default=0.0, description="Radiant total laning score")
    dire_laning_score: float = Field(default=0.0, description="Dire total laning score")

    hero_stats: List[HeroLanePhase] = Field(default_factory=list, description="Stats for each hero")
    rotations: List[LaneRotation] = Field(default_factory=list, description="All rotation events")
    wave_nukes: List[WaveNuke] = Field(default_factory=list, description="Wave pushing ability usage")
    neutral_aggro: List[NeutralAggro] = Field(default_factory=list, description="All neutral aggro events")
    tower_pressure: List[TowerPressure] = Field(default_factory=list, description="All tower damage events")

    error: Optional[str] = Field(default=None)
