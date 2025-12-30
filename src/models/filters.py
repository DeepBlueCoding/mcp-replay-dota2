"""
Unified filter models for MCP tools.

Provides Pydantic models for filtering events, combat data, and fights.
All filters support partial matching for location and hero names.

Usage:
    # Build filters from tool parameters
    filters = DeathFilters.from_params(killer="jugg", location="t1", start_time=300)

    # Apply to data
    filtered_deaths = filters.apply(deaths)
"""

from typing import TYPE_CHECKING, List, Optional, TypeVar

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..models.combat_log import AbilityUsage, FightParticipation, HeroDeath

T = TypeVar("T")


def _partial_match(filter_val: Optional[str], actual_val: Optional[str]) -> bool:
    """Case-insensitive partial string match."""
    if not filter_val:
        return True
    if not actual_val:
        return False
    return filter_val.lower() in actual_val.lower()


class TimeRange(BaseModel):
    """Time range filter for events."""

    start: Optional[float] = Field(default=None, description="Start time in seconds")
    end: Optional[float] = Field(default=None, description="End time in seconds")

    def contains(self, game_time: float) -> bool:
        """Check if game_time is within range."""
        if self.start is not None and game_time < self.start:
            return False
        if self.end is not None and game_time > self.end:
            return False
        return True


class EventFilters(BaseModel):
    """
    Base filters for any game event.

    Supports filtering by hero, location, and time range.
    All string filters use partial matching (case-insensitive).
    """

    hero: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    time_range: Optional[TimeRange] = Field(default=None)

    @classmethod
    def from_params(
        cls,
        hero: Optional[str] = None,
        location: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        **kwargs,
    ) -> "EventFilters":
        """Build filter from individual parameters."""
        time_range = None
        if start_time is not None or end_time is not None:
            time_range = TimeRange(start=start_time, end=end_time)
        return cls(hero=hero, location=location, time_range=time_range, **kwargs)

    def is_empty(self) -> bool:
        """Check if no filters are set."""
        return not any([self.hero, self.location, self.time_range])

    def matches_hero(self, hero_name: Optional[str]) -> bool:
        return _partial_match(self.hero, hero_name)

    def matches_location(self, location: Optional[str]) -> bool:
        return _partial_match(self.location, location)

    def matches_time(self, game_time: float) -> bool:
        if not self.time_range:
            return True
        return self.time_range.contains(game_time)


class CombatFilters(EventFilters):
    """Filters for combat events with ability filtering."""

    ability: Optional[str] = Field(default=None)

    @classmethod
    def from_params(  # type: ignore[override]
        cls,
        hero: Optional[str] = None,
        location: Optional[str] = None,
        ability: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        **kwargs,
    ) -> "CombatFilters":
        time_range = None
        if start_time is not None or end_time is not None:
            time_range = TimeRange(start=start_time, end=end_time)
        return cls(
            hero=hero, location=location, ability=ability, time_range=time_range, **kwargs
        )

    def is_empty(self) -> bool:
        return super().is_empty() and not self.ability

    def matches_ability(self, ability_name: Optional[str]) -> bool:
        return _partial_match(self.ability, ability_name)


class FightFilters(EventFilters):
    """Filters for fight/teamfight queries."""

    min_deaths: Optional[int] = Field(default=None)
    is_teamfight: Optional[bool] = Field(default=None)

    @classmethod
    def from_params(  # type: ignore[override]
        cls,
        location: Optional[str] = None,
        min_deaths: Optional[int] = None,
        is_teamfight: Optional[bool] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        **kwargs,
    ) -> "FightFilters":
        time_range = None
        if start_time is not None or end_time is not None:
            time_range = TimeRange(start=start_time, end=end_time)
        return cls(
            location=location,
            min_deaths=min_deaths,
            is_teamfight=is_teamfight,
            time_range=time_range,
            **kwargs,
        )

    def is_empty(self) -> bool:
        return (
            super().is_empty()
            and self.min_deaths is None
            and self.is_teamfight is None
        )

    def apply(self, fights: List[dict]) -> List[dict]:
        """Apply filters to a list of fight dicts."""
        if self.is_empty():
            return fights
        return [f for f in fights if self._matches_fight(f)]

    def _matches_fight(self, fight: dict) -> bool:
        if not self.matches_location(fight.get("location")):
            return False
        start_time = fight.get("start_time", 0.0)
        if not self.matches_time(start_time):
            return False
        if self.min_deaths is not None and fight.get("total_deaths", 0) < self.min_deaths:
            return False
        if self.is_teamfight is not None and fight.get("is_teamfight", False) != self.is_teamfight:
            return False
        return True


class DeathFilters(CombatFilters):
    """Filters for hero death queries."""

    killer: Optional[str] = Field(default=None)
    victim: Optional[str] = Field(default=None)

    @classmethod
    def from_params(  # type: ignore[override]
        cls,
        killer: Optional[str] = None,
        victim: Optional[str] = None,
        location: Optional[str] = None,
        ability: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        **kwargs,
    ) -> "DeathFilters":
        time_range = None
        if start_time is not None or end_time is not None:
            time_range = TimeRange(start=start_time, end=end_time)
        return cls(
            killer=killer,
            victim=victim,
            location=location,
            ability=ability,
            time_range=time_range,
            **kwargs,
        )

    def is_empty(self) -> bool:
        return super().is_empty() and not self.killer and not self.victim

    def apply(self, deaths: List["HeroDeath"]) -> List["HeroDeath"]:
        """Apply filters to a list of HeroDeath objects."""
        if self.is_empty():
            return deaths
        return [d for d in deaths if self._matches_death(d)]

    def _matches_death(self, death: "HeroDeath") -> bool:
        if not _partial_match(self.killer, death.killer):
            return False
        if not _partial_match(self.victim, death.victim):
            return False
        if not self.matches_ability(death.ability):
            return False
        if not self.matches_location(death.location):
            return False
        if not self.matches_time(death.game_time):
            return False
        return True


class HeroPerformanceFilters(CombatFilters):
    """Filters for hero performance queries with time range support."""

    @classmethod
    def from_params(  # type: ignore[override]
        cls,
        ability: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        **kwargs,
    ) -> "HeroPerformanceFilters":
        time_range = None
        if start_time is not None or end_time is not None:
            time_range = TimeRange(start=start_time, end=end_time)
        return cls(ability=ability, time_range=time_range, **kwargs)

    def apply_to_fights(
        self, fights: List["FightParticipation"]
    ) -> List["FightParticipation"]:
        """Apply time filters to a list of FightParticipation objects."""
        if self.is_empty():
            return fights
        return [f for f in fights if self._matches_fight(f)]

    def _matches_fight(self, fight: "FightParticipation") -> bool:
        """Check if fight matches time filter (based on fight_start)."""
        return self.matches_time(fight.fight_start)

    def recalculate_totals(
        self, filtered_fights: List["FightParticipation"]
    ) -> dict:
        """Recalculate totals from filtered fights list."""
        total_kills = sum(f.kills for f in filtered_fights)
        total_deaths = sum(f.deaths for f in filtered_fights)
        total_assists = sum(f.assists for f in filtered_fights)
        total_teamfights = sum(1 for f in filtered_fights if f.is_teamfight)
        total_fights = len(filtered_fights)

        return {
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "total_assists": total_assists,
            "total_teamfights": total_teamfights,
            "total_fights": total_fights,
        }

    def recalculate_ability_summary(
        self, filtered_fights: List["FightParticipation"]
    ) -> List["AbilityUsage"]:
        """Aggregate ability usage from filtered fights."""
        from ..models.combat_log import AbilityUsage

        ability_stats: dict = {}
        for fight in filtered_fights:
            for ability in fight.abilities_used:
                if ability.ability not in ability_stats:
                    ability_stats[ability.ability] = {
                        "total_casts": 0,
                        "hero_hits": 0,
                    }
                ability_stats[ability.ability]["total_casts"] += ability.total_casts
                ability_stats[ability.ability]["hero_hits"] += ability.hero_hits

        result = []
        for ability_name, stats in ability_stats.items():
            casts = stats["total_casts"]
            hits = stats["hero_hits"]
            hit_rate = (hits / casts * 100) if casts > 0 else 0.0
            result.append(
                AbilityUsage(
                    ability=ability_name,
                    total_casts=casts,
                    hero_hits=hits,
                    hit_rate=round(hit_rate, 1),
                )
            )

        # Sort by total_casts descending
        result.sort(key=lambda x: x.total_casts, reverse=True)
        return result
