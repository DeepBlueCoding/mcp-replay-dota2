"""
Fight detector analyzer - detects fights from combat activity.

Uses combat intensity (hero-to-hero damage, abilities, deaths) rather than
just deaths to identify fights. This catches teamfights where teams disengage
before anyone dies, and properly captures the initiation phase.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set

from ..models.combat_data import CombatLogEvent, Fight, FightResult, HeroDeath

logger = logging.getLogger(__name__)

# Fight detection parameters
COMBAT_GAP_SECONDS = 8.0  # Max gap between INTENSE combat to be same fight
INTENSITY_WINDOW = 3.0  # Seconds to measure combat intensity
MIN_INTENSITY_EVENTS = 5  # Minimum events per intensity window to continue fight
MIN_FIGHT_HEROES = 3  # Minimum unique heroes involved for a fight
MIN_FIGHT_ABILITIES = 2  # Minimum abilities used (not just right-clicks)
MIN_FIGHT_DURATION = 3.0  # Minimum sustained combat duration
HARASSMENT_MAX_EVENTS = 8  # Below this = harassment, not a fight
TEAMFIGHT_THRESHOLD = 3  # Minimum deaths for teamfight classification

# Abilities that indicate serious combat (not just poke)
SERIOUS_COMBAT_ABILITIES = {
    # Big ultimates
    "faceless_void_chronosphere", "enigma_black_hole", "magnataur_reverse_polarity",
    "tidehunter_ravage", "earthshaker_echo_slam", "warlock_rain_of_chaos",
    "medusa_stone_gaze", "nevermore_requiem", "crystal_maiden_freezing_field",
    "witch_doctor_death_ward", "phoenix_supernova", "disruptor_static_storm",
    # Stuns and disables
    "earthshaker_fissure", "lion_impale", "lina_light_strike_array",
    "sand_king_burrowstrike", "centaur_hoof_stomp", "slardar_slithereen_crush",
    "axe_berserkers_call", "mars_arena_of_blood", "puck_dream_coil",
    # High-commit abilities
    "item_black_king_bar", "item_blink", "item_swift_blink", "item_arcane_blink",
    "item_overwhelming_blink",
}


@dataclass
class CombatWindow:
    """A window of combat activity."""

    start_time: float = 0.0
    end_time: float = 0.0
    heroes_involved: Set[str] = field(default_factory=set)
    abilities_used: Set[str] = field(default_factory=set)
    serious_abilities: Set[str] = field(default_factory=set)
    event_count: int = 0
    damage_events: int = 0
    deaths: List[HeroDeath] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def hero_count(self) -> int:
        return len(self.heroes_involved)

    @property
    def has_deaths(self) -> bool:
        return len(self.deaths) > 0

    def is_real_fight(self) -> bool:
        """Determine if this combat window represents a real fight (not harassment)."""
        # Any death = definitely a fight
        if self.has_deaths:
            return True

        # Need enough heroes involved
        if self.hero_count < MIN_FIGHT_HEROES:
            return False

        # Need enough ability usage OR sustained duration
        if len(self.serious_abilities) >= 1:
            return True

        if len(self.abilities_used) >= MIN_FIGHT_ABILITIES and self.duration >= MIN_FIGHT_DURATION:
            return True

        # Too few events = just harassment
        if self.event_count < HARASSMENT_MAX_EVENTS:
            return False

        # Sustained combat with multiple heroes
        if self.duration >= MIN_FIGHT_DURATION and self.damage_events >= 10:
            return True

        return False


class FightDetector:
    """
    Detects fights from combat log events.

    Algorithm:
    1. Scan combat log for hero-to-hero combat events
    2. Group events into combat windows based on time proximity
    3. Filter out harassment (brief, low-intensity exchanges)
    4. Classify remaining windows as fights
    """

    def __init__(
        self,
        combat_gap: float = COMBAT_GAP_SECONDS,
        teamfight_threshold: int = TEAMFIGHT_THRESHOLD,
    ):
        self.combat_gap = combat_gap
        self.teamfight_threshold = teamfight_threshold

    def _format_time(self, seconds: float) -> str:
        """Format game time as M:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def _clean_hero_name(self, name: str) -> str:
        """Remove npc_dota_hero_ prefix."""
        if name and name.startswith("npc_dota_hero_"):
            return name[14:]
        return name or ""

    def _is_hero_combat_event(self, event: CombatLogEvent) -> bool:
        """Check if event represents hero-to-hero combat."""
        # Must involve at least one hero
        if not event.attacker_is_hero and not event.target_is_hero:
            return False

        # Damage or ability on hero target
        if event.type in ("DAMAGE", "ABILITY") and event.target_is_hero:
            return True

        # Item usage by hero (BKB, Blink, etc.)
        if event.type == "ITEM" and event.attacker_is_hero:
            return True

        return False

    def detect_fights_from_combat(
        self,
        events: List[CombatLogEvent],
        deaths: Optional[List[HeroDeath]] = None,
    ) -> FightResult:
        """
        Detect fights from combat log events.

        Args:
            events: Combat log events (should include DAMAGE, ABILITY, ITEM)
            deaths: Optional list of deaths to associate with fights

        Returns:
            FightResult with detected fights
        """
        if not events:
            return FightResult()

        # Build combat windows
        windows = self._build_combat_windows(events)

        # Associate deaths with windows
        if deaths:
            self._associate_deaths(windows, deaths)

        # Filter out harassment and convert to fights
        fights = []
        fight_counter = 0

        for window in windows:
            if window.is_real_fight():
                fight_counter += 1
                fight = self._window_to_fight(window, fight_counter)
                fights.append(fight)

        # Calculate statistics
        total_deaths = sum(len(f.deaths) for f in fights)
        teamfights = sum(1 for f in fights if f.total_deaths >= self.teamfight_threshold)

        return FightResult(
            fights=fights,
            total_deaths=total_deaths,
            total_fights=len(fights),
            teamfights=teamfights,
        )

    def _build_combat_windows(self, events: List[CombatLogEvent]) -> List[CombatWindow]:
        """
        Group combat events into intensity-based windows.

        Uses combat intensity (events per second) to determine fight boundaries,
        not just time gaps. This separates sustained poke/siege from real fights.
        """
        # Filter to hero combat events
        combat_events = [e for e in events if self._is_hero_combat_event(e)]

        if not combat_events:
            return []

        # Sort by time
        combat_events.sort(key=lambda e: e.game_time)

        windows = []
        current = CombatWindow()
        current.start_time = combat_events[0].game_time
        current.end_time = combat_events[0].game_time
        recent_events: List[float] = []  # Track event times for intensity calc

        for event in combat_events:
            event_time = event.game_time

            # Remove old events from intensity tracking
            recent_events = [t for t in recent_events if event_time - t <= INTENSITY_WINDOW]

            # Calculate gap since last event
            gap = event_time - current.end_time if current.event_count > 0 else 0

            # Decide if this event starts a new window
            should_split = False

            if gap > self.combat_gap:
                # Long gap = definitely split
                should_split = True
            elif gap > INTENSITY_WINDOW and len(recent_events) < MIN_INTENSITY_EVENTS:
                # Medium gap with low recent intensity = split
                should_split = True

            if should_split and current.event_count > 0:
                # Save current window
                windows.append(current)
                # Start new window
                current = CombatWindow()
                current.start_time = event_time
                recent_events = []

            # Update current window
            current.end_time = event_time
            current.event_count += 1
            recent_events.append(event_time)

            # Track heroes involved
            if event.attacker_is_hero:
                current.heroes_involved.add(self._clean_hero_name(event.attacker))
            if event.target_is_hero:
                current.heroes_involved.add(self._clean_hero_name(event.target))

            # Track abilities
            ability = event.ability
            if ability and ability not in ("dota_unknown", "attack"):
                current.abilities_used.add(ability)
                if ability in SERIOUS_COMBAT_ABILITIES:
                    current.serious_abilities.add(ability)

            # Count damage events
            if event.type == "DAMAGE":
                current.damage_events += 1

        # Don't forget last window
        if current.event_count > 0:
            windows.append(current)

        return windows

    def _associate_deaths(self, windows: List[CombatWindow], deaths: List[HeroDeath]):
        """Associate deaths with their combat windows."""
        for death in deaths:
            death_time = death.game_time

            # Find window containing this death
            for window in windows:
                # Death within window or shortly after (grace period for kill attribution)
                if window.start_time - 2.0 <= death_time <= window.end_time + 2.0:
                    window.deaths.append(death)
                    # Add killer and victim to participants
                    window.heroes_involved.add(self._clean_hero_name(death.victim))
                    if death.killer_is_hero:
                        window.heroes_involved.add(self._clean_hero_name(death.killer))
                    break

    def _window_to_fight(self, window: CombatWindow, fight_number: int) -> Fight:
        """Convert a CombatWindow to a Fight."""
        return Fight(
            fight_id=f"fight_{fight_number}",
            start_time=window.start_time,
            start_time_str=self._format_time(window.start_time),
            end_time=window.end_time,
            end_time_str=self._format_time(window.end_time),
            duration=window.duration,
            deaths=window.deaths,
            participants=sorted(list(window.heroes_involved)),
            radiant_deaths=0,  # Would need team mapping
            dire_deaths=0,
        )

    # Legacy methods for backward compatibility with death-based detection

    def detect_fights(self, deaths: List[HeroDeath]) -> FightResult:
        """
        Legacy method: Detect fights from deaths only.

        For full combat-based detection, use detect_fights_from_combat().
        This method uses simple death clustering for backward compatibility.
        """
        if not deaths:
            return FightResult()

        # Sort by game time
        sorted_deaths = sorted(deaths, key=lambda d: d.game_time)

        fights = []
        current_fight_deaths: List[HeroDeath] = []
        fight_counter = 0
        fight_window = 15.0  # Legacy 15s window for death clustering

        for death in sorted_deaths:
            if not current_fight_deaths:
                current_fight_deaths.append(death)
            elif death.game_time - current_fight_deaths[-1].game_time <= fight_window:
                current_fight_deaths.append(death)
            else:
                if current_fight_deaths:
                    fight_counter += 1
                    fight = self._create_fight_from_deaths(current_fight_deaths, fight_counter)
                    fights.append(fight)
                current_fight_deaths = [death]

        if current_fight_deaths:
            fight_counter += 1
            fight = self._create_fight_from_deaths(current_fight_deaths, fight_counter)
            fights.append(fight)

        teamfights = sum(1 for f in fights if f.is_teamfight)

        return FightResult(
            fights=fights,
            total_deaths=len(sorted_deaths),
            total_fights=len(fights),
            teamfights=teamfights,
        )

    def _create_fight_from_deaths(self, deaths: List[HeroDeath], fight_number: int) -> Fight:
        """Create a Fight object from deaths (legacy method)."""
        start_time = deaths[0].game_time
        end_time = deaths[-1].game_time

        participants: Set[str] = set()
        for death in deaths:
            participants.add(self._clean_hero_name(death.victim))
            if death.killer_is_hero:
                participants.add(self._clean_hero_name(death.killer))

        return Fight(
            fight_id=f"fight_{fight_number}",
            start_time=start_time,
            start_time_str=self._format_time(start_time),
            end_time=end_time,
            end_time_str=self._format_time(end_time),
            duration=end_time - start_time,
            deaths=deaths,
            participants=sorted(list(participants)),
            radiant_deaths=0,
            dire_deaths=0,
        )

    def get_fight_at_time(
        self,
        deaths: List[HeroDeath],
        reference_time: float,
        hero: Optional[str] = None,
    ) -> Optional[Fight]:
        """
        Find the fight closest to a reference time (legacy death-based).

        For combat-based detection, use get_fight_at_time_from_combat().
        """
        result = self.detect_fights(deaths)

        if not result.fights:
            return None

        best_fight = None
        best_distance = float('inf')

        for fight in result.fights:
            # Check if reference_time is within or near fight
            if fight.start_time - 5.0 <= reference_time <= fight.end_time + 15.0:
                if hero:
                    hero_lower = hero.lower()
                    if any(hero_lower in p.lower() for p in fight.participants):
                        return fight
                else:
                    return fight

            mid_time = (fight.start_time + fight.end_time) / 2
            distance = abs(mid_time - reference_time)
            if distance < best_distance:
                if hero:
                    hero_lower = hero.lower()
                    if any(hero_lower in p.lower() for p in fight.participants):
                        best_distance = distance
                        best_fight = fight
                else:
                    best_distance = distance
                    best_fight = fight

        return best_fight

    def get_fight_at_time_from_combat(
        self,
        events: List[CombatLogEvent],
        deaths: List[HeroDeath],
        reference_time: float,
        hero: Optional[str] = None,
    ) -> Optional[Fight]:
        """
        Find fight at reference time using combat-based detection.

        Args:
            events: Combat log events
            deaths: Hero deaths
            reference_time: Game time to search around
            hero: Optional hero filter

        Returns:
            Fight containing reference_time, or None
        """
        result = self.detect_fights_from_combat(events, deaths)

        if not result.fights:
            return None

        best_fight = None
        best_distance = float('inf')

        for fight in result.fights:
            # Check if reference_time is within fight (with buffer)
            if fight.start_time - 3.0 <= reference_time <= fight.end_time + 5.0:
                if hero:
                    hero_lower = hero.lower()
                    if any(hero_lower in p.lower() for p in fight.participants):
                        return fight
                else:
                    return fight

            mid_time = (fight.start_time + fight.end_time) / 2
            distance = abs(mid_time - reference_time)
            if distance < best_distance:
                if hero:
                    hero_lower = hero.lower()
                    if any(hero_lower in p.lower() for p in fight.participants):
                        best_distance = distance
                        best_fight = fight
                else:
                    best_distance = distance
                    best_fight = fight

        return best_fight

    def get_teamfights(self, deaths: List[HeroDeath]) -> List[Fight]:
        """Get only teamfights (3+ deaths) - legacy method."""
        result = self.detect_fights(deaths)
        return [f for f in result.fights if f.is_teamfight]

    def get_skirmishes(self, deaths: List[HeroDeath]) -> List[Fight]:
        """Get only skirmishes (1-2 deaths) - legacy method."""
        result = self.detect_fights(deaths)
        return [f for f in result.fights if not f.is_teamfight]
