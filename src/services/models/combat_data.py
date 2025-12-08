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
class Buyback:
    """A buyback event."""

    game_time: float
    game_time_str: str
    hero: str
    player_slot: int
    death_time: Optional[float] = None  # When they died (for fast buyback calc)
    buyback_delay: Optional[float] = None  # Seconds between death and buyback


@dataclass
class GenericAoEHit:
    """Any ability that hit 3+ heroes (not just 'big' abilities)."""

    game_time: float
    game_time_str: str
    ability: str
    caster: str
    targets: List[str] = field(default_factory=list)
    hero_count: int = 0


@dataclass
class ClutchSave:
    """A clutch save - hero survives lethal situation via item/ability."""

    game_time: float
    game_time_str: str
    saved_hero: str
    save_type: str  # "self_banish", "ally_glimmer", "ally_lotus", "linken_block", etc.
    save_ability: str  # The item/ability used
    saved_from: Optional[str] = None  # The ability they were saved from (e.g., "omnislash")
    saver: Optional[str] = None  # Who saved them (None if self-save)


@dataclass
class BKBBlinkCombo:
    """A BKB + Blink combo into big ability."""

    game_time: float
    game_time_str: str
    hero: str
    ability: str  # The big ability cast after BKB+Blink
    ability_display: str
    bkb_time: float  # When BKB was used
    blink_time: float  # When Blink was used
    is_initiator: bool = False  # True if first BKB+Blink combo in the fight


@dataclass
class CoordinatedUltimates:
    """Multiple heroes using big ultimates together."""

    game_time: float
    game_time_str: str
    heroes: List[str] = field(default_factory=list)
    abilities: List[str] = field(default_factory=list)
    window_seconds: float = 0.0  # How tight the coordination was


@dataclass
class RefresherCombo:
    """A hero using Refresher to double-cast an ultimate."""

    game_time: float
    game_time_str: str
    hero: str
    ability: str
    ability_display: str
    first_cast_time: float
    second_cast_time: float


@dataclass
class FightHighlights:
    """Key moments extracted from a fight."""

    # Big teamfight abilities (Chrono, Black Hole, etc.) - kept for backwards compat
    multi_hero_abilities: List[MultiHeroAbility] = field(default_factory=list)

    # Native Valve events
    kill_streaks: List[KillStreak] = field(default_factory=list)
    team_wipes: List[TeamWipe] = field(default_factory=list)

    # Generic 3+ hero hits (any ability)
    generic_aoe_hits: List[GenericAoEHit] = field(default_factory=list)

    # Buybacks during fight
    buybacks: List[Buyback] = field(default_factory=list)

    # Clutch saves (self-banish, ally Glimmer, etc.)
    clutch_saves: List[ClutchSave] = field(default_factory=list)

    # BKB + Blink combos (first is initiator, rest are follow-ups)
    bkb_blink_combos: List[BKBBlinkCombo] = field(default_factory=list)

    # Coordinated ultimates (2+ heroes ulting together)
    coordinated_ults: List[CoordinatedUltimates] = field(default_factory=list)

    # Refresher double ultimates
    refresher_combos: List[RefresherCombo] = field(default_factory=list)

    # Legacy initiation detection (single hero)
    fight_initiator: Optional[str] = None
    initiation_ability: Optional[str] = None
