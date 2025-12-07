"""
Data models for combat analysis.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HeroDeath:
    """A hero death event."""

    game_time: float
    game_time_str: str
    tick: int
    killer: str
    victim: str
    killer_is_hero: bool
    ability: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    location_description: Optional[str] = None


@dataclass
class DamageEvent:
    """A damage event from combat log."""

    game_time: float
    tick: int
    attacker: str
    target: str
    damage: int
    ability: Optional[str] = None
    attacker_is_hero: bool = False
    target_is_hero: bool = False


@dataclass
class Fight:
    """A fight containing one or more hero deaths."""

    fight_id: str
    start_time: float
    start_time_str: str
    end_time: float
    end_time_str: str
    duration: float
    deaths: List[HeroDeath] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    radiant_deaths: int = 0
    dire_deaths: int = 0

    @property
    def total_deaths(self) -> int:
        return len(self.deaths)

    @property
    def is_teamfight(self) -> bool:
        return self.total_deaths >= 3


@dataclass
class FightResult:
    """Result of fight detection analysis."""

    fights: List[Fight] = field(default_factory=list)
    total_deaths: int = 0
    total_fights: int = 0
    teamfights: int = 0

    @property
    def skirmishes(self) -> int:
        return self.total_fights - self.teamfights


@dataclass
class ItemPurchase:
    """An item purchase event."""

    game_time: float
    game_time_str: str
    tick: int
    hero: str
    item: str


@dataclass
class RunePickup:
    """A rune pickup event."""

    game_time: float
    game_time_str: str
    tick: int
    hero: str
    rune_type: str


@dataclass
class ObjectiveKill:
    """An objective kill (Roshan, tower, barracks, etc.)."""

    game_time: float
    game_time_str: str
    tick: int
    objective_type: str
    objective_name: str
    killer: Optional[str] = None
    team: Optional[str] = None
    extra_info: Optional[dict] = None


@dataclass
class CourierKill:
    """A courier kill event."""

    game_time: float
    game_time_str: str
    tick: int
    killer: str
    killer_is_hero: bool
    owner: str
    team: str
    position_x: Optional[float] = None
    position_y: Optional[float] = None


@dataclass
class CombatLogEvent:
    """A combat log event for the get_combat_log tool."""

    type: str
    game_time: float
    game_time_str: str
    tick: int
    attacker: str
    attacker_is_hero: bool
    target: str
    target_is_hero: bool
    ability: Optional[str] = None
    value: Optional[int] = None
    hit: Optional[bool] = None


@dataclass
class MultiHeroAbility:
    """A big ability that hit multiple heroes."""

    game_time: float
    game_time_str: str
    ability: str
    ability_display: str
    caster: str
    targets: List[str] = field(default_factory=list)
    hero_count: int = 0


@dataclass
class KillStreak:
    """A kill streak (double kill, rampage, etc.)."""

    game_time: float
    game_time_str: str
    hero: str
    streak_type: str  # "double_kill", "triple_kill", "ultra_kill", "rampage"
    kills: int = 0
    victims: List[str] = field(default_factory=list)


@dataclass
class TeamWipe:
    """An ace / team wipe."""

    game_time: float
    game_time_str: str
    team_wiped: str  # "radiant" or "dire"
    duration: float  # seconds to wipe all 5
    killer_team: str


@dataclass
class FightHighlights:
    """Key moments extracted from a fight."""

    multi_hero_abilities: List[MultiHeroAbility] = field(default_factory=list)
    kill_streaks: List[KillStreak] = field(default_factory=list)
    team_wipes: List[TeamWipe] = field(default_factory=list)
    fight_initiator: Optional[str] = None  # hero who started the fight
    initiation_ability: Optional[str] = None  # ability used to initiate
