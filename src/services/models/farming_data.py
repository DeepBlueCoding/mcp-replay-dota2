"""
Data models for farming pattern analysis.

Provides minute-by-minute breakdown of creep kills, positions, and farm efficiency.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from src.models.types import CoercedInt


class CreepKill(BaseModel):
    """A single creep kill event."""

    game_time: float = Field(description="Game time in seconds")
    game_time_str: str = Field(description="Game time formatted as M:SS")
    creep_name: str = Field(description="Full creep name")
    creep_type: str = Field(description="Creep type: lane, neutral, or other")
    neutral_camp: Optional[str] = Field(
        default=None,
        description="Neutral camp type if applicable (e.g., 'large_troll', 'ancient_black_dragon')"
    )
    camp_tier: Optional[str] = Field(
        default=None,
        description="Camp tier from python-manta: 'small', 'medium', 'hard', or 'ancient'"
    )
    position_x: Optional[float] = Field(
        default=None, description="X coordinate where the kill occurred"
    )
    position_y: Optional[float] = Field(
        default=None, description="Y coordinate where the kill occurred"
    )
    map_area: Optional[str] = Field(
        default=None,
        description="Map area where kill occurred (e.g., 'dire_jungle', 'radiant_jungle', 'radiant_safelane')"
    )


class MapPositionSnapshot(BaseModel):
    """A position snapshot on the map."""

    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")
    area: str = Field(description="Map area (e.g., 'dire_jungle', 'radiant_safelane')")


class CampClear(BaseModel):
    """A single neutral camp clear within a minute."""

    time_str: str = Field(description="Game time formatted as M:SS")
    camp: str = Field(description="Camp type (e.g., 'large_troll', 'medium_satyr')")
    tier: str = Field(description="Camp tier: small, medium, large, or ancient")
    area: str = Field(description="Map area where camp was cleared")
    position_x: Optional[float] = Field(default=None, description="X coordinate")
    position_y: Optional[float] = Field(default=None, description="Y coordinate")
    creeps_killed: int = Field(default=1, description="Number of creeps killed in this camp")


class WaveClear(BaseModel):
    """A lane creep wave clear event (grouped lane creeps killed in quick succession)."""

    time_str: str = Field(description="Game time when wave was cleared (M:SS)")
    creeps_killed: int = Field(description="Number of lane creeps killed in this wave")
    position_x: Optional[float] = Field(default=None, description="X coordinate")
    position_y: Optional[float] = Field(default=None, description="Y coordinate")
    area: str = Field(description="Map area (e.g., 'radiant_safelane', 'mid_lane')")


class MultiCampClear(BaseModel):
    """Multiple camps cleared simultaneously (stacked or adjacent camps)."""

    time_str: str = Field(description="Game time when multi-camp clear started (M:SS)")
    camps: List[str] = Field(description="List of camp types cleared together")
    duration_seconds: float = Field(description="Time span of all kills in this clear")
    creeps_killed: CoercedInt = Field(description="Total creeps killed across all camps")
    area: str = Field(description="Map area where multi-camp clear occurred")


class MinuteFarmingData(BaseModel):
    """Farming data for a single minute."""

    minute: CoercedInt = Field(description="Game minute")

    # Position at minute boundaries
    position_at_start: Optional[MapPositionSnapshot] = Field(
        default=None, description="Hero position at the start of this minute (X:00)"
    )
    position_at_end: Optional[MapPositionSnapshot] = Field(
        default=None, description="Hero position at the end of this minute (X:59)"
    )

    # Ordered farming events - shows farming route with positions
    camp_sequence: List[CampClear] = Field(
        default_factory=list,
        description="Ordered sequence of neutral camps cleared during this minute"
    )
    wave_clears: List[WaveClear] = Field(
        default_factory=list,
        description="Lane wave clear events during this minute"
    )

    # Summary counts
    lane_creeps_killed: CoercedInt = Field(
        default=0, description="Lane creeps killed during this minute"
    )
    camps_cleared: CoercedInt = Field(
        default=0, description="Number of neutral camps cleared during this minute"
    )

    # Stats at end of minute
    gold: CoercedInt = Field(default=0, description="Net worth at end of minute")
    last_hits: CoercedInt = Field(default=0, description="Total last hits at end of minute")
    level: CoercedInt = Field(default=1, description="Hero level at end of minute")


class LevelTiming(BaseModel):
    """Timing for when a hero reached a specific level."""

    level: CoercedInt = Field(description="Hero level reached")
    time: float = Field(description="Game time in seconds")
    time_str: str = Field(description="Game time formatted as M:SS")


class ItemTiming(BaseModel):
    """Timing for when an item was purchased."""

    item: str = Field(description="Item name")
    time: float = Field(description="Game time in seconds when purchased")
    time_str: str = Field(description="Game time formatted as M:SS")


class FarmingTransitions(BaseModel):
    """Key transition points in farming pattern."""

    first_jungle_kill_time: Optional[float] = Field(
        default=None, description="Game time of first neutral creep kill (seconds)"
    )
    first_jungle_kill_str: Optional[str] = Field(
        default=None, description="Game time of first neutral creep kill (M:SS)"
    )
    first_large_camp_time: Optional[float] = Field(
        default=None, description="Game time of first large/ancient camp kill"
    )
    first_large_camp_str: Optional[str] = Field(
        default=None, description="Game time of first large camp kill (M:SS)"
    )
    left_lane_time: Optional[float] = Field(
        default=None, description="Game time when hero first moved to jungle for extended farm"
    )
    left_lane_str: Optional[str] = Field(
        default=None, description="Game time when left lane (M:SS)"
    )


class FarmingSummary(BaseModel):
    """Summary statistics for farming pattern."""

    total_lane_creeps: CoercedInt = Field(
        default=0, description="Total lane creeps killed in the time range"
    )
    total_neutral_creeps: CoercedInt = Field(
        default=0, description="Total neutral creeps killed in the time range"
    )
    jungle_percentage: float = Field(
        default=0.0, description="Percentage of farm from jungle (0-100)"
    )
    gpm: float = Field(default=0.0, description="Gold per minute in the time range")
    cs_per_min: float = Field(
        default=0.0, description="Creep score per minute in the time range"
    )
    camps_cleared: Dict[str, int] = Field(
        default_factory=dict,
        description="Total neutral kills by camp type"
    )
    multi_camp_clears: CoercedInt = Field(
        default=0, description="Number of times hero farmed 2+ camps simultaneously"
    )


class FarmingPatternResponse(BaseModel):
    """Response for get_farming_pattern tool."""

    success: bool
    match_id: int
    hero: str = Field(description="Hero name analyzed")
    start_minute: CoercedInt = Field(description="Start of analysis range")
    end_minute: CoercedInt = Field(description="End of analysis range")

    # Power spike tracking
    level_timings: List[LevelTiming] = Field(
        default_factory=list,
        description="When hero reached each level (for power spike analysis)"
    )
    item_timings: List[ItemTiming] = Field(
        default_factory=list,
        description="When items were purchased (for power spike analysis)"
    )

    # Per-minute farming data with routes
    minutes: List[MinuteFarmingData] = Field(
        default_factory=list,
        description="Minute-by-minute farming breakdown with camp sequences"
    )

    transitions: FarmingTransitions = Field(
        default_factory=FarmingTransitions,
        description="Key transition points in farming pattern"
    )
    summary: FarmingSummary = Field(
        default_factory=FarmingSummary,
        description="Summary statistics"
    )
    multi_camp_clears: List[MultiCampClear] = Field(
        default_factory=list,
        description="Events where hero farmed 2+ camps simultaneously (stacked/adjacent)"
    )
    error: Optional[str] = Field(default=None)
