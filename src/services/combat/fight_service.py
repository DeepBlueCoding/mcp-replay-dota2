"""
Fight service - high-level API for fight analysis.

Combines CombatService and FightDetector for convenient fight queries.
Uses combat-intensity based detection to catch fights without deaths.
"""

import logging
from typing import List, Optional, Set

from ...models.combat_log import DetailLevel
from ..analyzers.fight_analyzer import FightAnalyzer
from ..analyzers.fight_detector import FightDetector
from ..models.combat_data import Fight, FightResult, HeroDeath
from ..models.replay_data import ParsedReplayData
from .combat_service import CombatService

logger = logging.getLogger(__name__)


class FightService:
    """
    High-level service for fight analysis.

    Provides:
    - List all fights in a match
    - Get specific fight by ID or time
    - Get teamfights only
    - Get fight context (deaths + damage around a fight)
    """

    def __init__(
        self,
        combat_service: Optional[CombatService] = None,
        fight_detector: Optional[FightDetector] = None,
        fight_analyzer: Optional[FightAnalyzer] = None,
    ):
        self._combat = combat_service or CombatService()
        self._detector = fight_detector or FightDetector()
        self._analyzer = fight_analyzer or FightAnalyzer()

    def get_all_fights(self, data: ParsedReplayData) -> FightResult:
        """
        Get all fights in a match (legacy death-based detection).

        Args:
            data: ParsedReplayData from ReplayService

        Returns:
            FightResult with all fights, statistics
        """
        deaths = self._combat.get_hero_deaths(data)
        return self._detector.detect_fights(deaths)

    def get_all_fights_from_combat(self, data: ParsedReplayData) -> FightResult:
        """
        Get all fights using combat-intensity based detection.

        This method detects fights based on hero-to-hero combat activity,
        not just deaths. It catches teamfights where teams disengage before
        anyone dies, and properly captures the initiation phase.

        Args:
            data: ParsedReplayData from ReplayService

        Returns:
            FightResult with detected fights
        """
        # Get all combat events (DAMAGE, ABILITY, ITEM)
        all_events = self._combat.get_combat_log(data, detail_level=DetailLevel.FULL)
        deaths = self._combat.get_hero_deaths(data)
        return self._detector.detect_fights_from_combat(all_events, deaths)

    def get_fight_by_id(
        self,
        data: ParsedReplayData,
        fight_id: str,
    ) -> Optional[Fight]:
        """
        Get a specific fight by ID.

        Args:
            data: ParsedReplayData from ReplayService
            fight_id: Fight ID (e.g., "fight_1")

        Returns:
            Fight if found, None otherwise
        """
        result = self.get_all_fights(data)
        for fight in result.fights:
            if fight.fight_id == fight_id:
                return fight
        return None

    def get_fight_at_time(
        self,
        data: ParsedReplayData,
        reference_time: float,
        hero: Optional[str] = None,
    ) -> Optional[Fight]:
        """
        Get the fight at or near a specific time.

        Args:
            data: ParsedReplayData from ReplayService
            reference_time: Game time in seconds
            hero: Optional hero to anchor (must be involved)

        Returns:
            Fight if found, None otherwise
        """
        deaths = self._combat.get_hero_deaths(data)
        return self._detector.get_fight_at_time(deaths, reference_time, hero)

    def get_teamfights(
        self,
        data: ParsedReplayData,
        min_deaths: int = 3,
    ) -> List[Fight]:
        """
        Get only teamfights (3+ deaths by default).

        Args:
            data: ParsedReplayData from ReplayService
            min_deaths: Minimum deaths to classify as teamfight

        Returns:
            List of teamfights
        """
        result = self.get_all_fights(data)
        return [f for f in result.fights if f.total_deaths >= min_deaths]

    def _get_fight_location(self, fight: Fight) -> Optional[str]:
        """
        Get the location where a fight took place based on first death position.

        Args:
            fight: Fight with deaths

        Returns:
            Location string (e.g., "radiant_jungle", "dire_t1_mid") or None if no position data
        """
        from ...utils.position_tracker import classify_map_position

        for death in fight.deaths:
            if death.position_x is not None and death.position_y is not None:
                position = classify_map_position(death.position_x, death.position_y)
                return position.region
        return None

    def get_fight_summary(self, data: ParsedReplayData) -> dict:
        """
        Get a summary of all fights in the match.

        Args:
            data: ParsedReplayData from ReplayService

        Returns:
            Dictionary with fight statistics and full fight data
        """
        result = self.get_all_fights(data)

        return {
            "total_fights": result.total_fights,
            "teamfights": result.teamfights,
            "skirmishes": result.skirmishes,
            "total_deaths": result.total_deaths,
            "fights": [
                {
                    "fight_id": f.fight_id,
                    "start_time": f.start_time,
                    "start_time_str": f.start_time_str,
                    "end_time": f.end_time,
                    "end_time_str": f.end_time_str,
                    "duration_seconds": round(f.duration, 1),
                    "total_deaths": f.total_deaths,
                    "participants": f.participants,
                    "is_teamfight": f.is_teamfight,
                    "location": self._get_fight_location(f),
                    "deaths": [
                        {
                            "game_time": d.game_time,
                            "game_time_str": d.game_time_str,
                            "killer": d.killer,
                            "victim": d.victim,
                            "ability": d.ability,
                        }
                        for d in f.deaths
                    ],
                }
                for f in result.fights
            ],
        }

    def get_deaths_in_fight(
        self,
        data: ParsedReplayData,
        fight_id: str,
    ) -> List[HeroDeath]:
        """
        Get all deaths in a specific fight.

        Args:
            data: ParsedReplayData from ReplayService
            fight_id: Fight ID

        Returns:
            List of HeroDeath events in the fight
        """
        fight = self.get_fight_by_id(data, fight_id)
        if fight:
            return fight.deaths
        return []

    def get_hero_fights(
        self,
        data: ParsedReplayData,
        hero: str,
    ) -> List[Fight]:
        """
        Get all fights a hero was involved in.

        Args:
            data: ParsedReplayData from ReplayService
            hero: Hero name to search for

        Returns:
            List of fights involving the hero
        """
        result = self.get_all_fights(data)
        hero_lower = hero.lower()

        return [
            f for f in result.fights
            if any(hero_lower in p.lower() for p in f.participants)
        ]

    def _filter_events_by_detail_level(
        self,
        events: List,
        detail_level: DetailLevel,
        max_events: Optional[int] = None,
    ) -> List:
        """
        Filter already-loaded CombatLogEvent list by detail level.

        Args:
            events: Pre-filtered CombatLogEvent list (already time-filtered)
            detail_level: NARRATIVE, TACTICAL, or FULL
            max_events: Maximum events to return

        Returns:
            Filtered list of events
        """
        if detail_level == DetailLevel.FULL:
            filtered = events
        else:
            filtered = []
            for e in events:
                if detail_level == DetailLevel.NARRATIVE:
                    if e.type == "DEATH" and e.target_is_hero:
                        filtered.append(e)
                    elif e.type == "ABILITY" and e.attacker_is_hero:
                        filtered.append(e)
                    elif e.type == "ITEM" and e.attacker_is_hero:
                        filtered.append(e)
                    elif e.type in ("PURCHASE", "BUYBACK"):
                        filtered.append(e)
                    elif e.type == "INTERRUPT_CHANNEL" and e.target_is_hero:
                        filtered.append(e)
                elif detail_level == DetailLevel.TACTICAL:
                    if e.type == "DEATH" and e.target_is_hero:
                        filtered.append(e)
                    elif e.type == "ABILITY" and e.attacker_is_hero:
                        filtered.append(e)
                    elif e.type == "ITEM" and e.attacker_is_hero:
                        filtered.append(e)
                    elif e.type in ("PURCHASE", "BUYBACK"):
                        filtered.append(e)
                    elif e.type == "DAMAGE" and e.attacker_is_hero and e.target_is_hero:
                        filtered.append(e)
                    elif e.type == "MODIFIER_ADD" and e.target_is_hero:
                        filtered.append(e)
                    elif e.type == "INTERRUPT_CHANNEL" and e.target_is_hero:
                        filtered.append(e)

        if max_events is not None and len(filtered) > max_events:
            filtered = filtered[:max_events]

        return filtered

    def _get_team_heroes(self, data: ParsedReplayData) -> tuple:
        """
        Extract radiant and dire hero sets from entity snapshots.

        Returns:
            Tuple of (radiant_heroes: Set[str], dire_heroes: Set[str])
        """
        radiant_heroes: Set[str] = set()
        dire_heroes: Set[str] = set()

        # Find a snapshot after laning phase starts (game_time > 60s)
        # The first snapshot may not have all heroes spawned yet
        for snapshot in data.entity_snapshots:
            if snapshot.game_time < 60:
                continue

            if hasattr(snapshot, 'heroes') and snapshot.heroes:
                for hero_snap in snapshot.heroes:
                    hero_name = hero_snap.hero_name
                    if hero_name and hero_name.startswith("npc_dota_hero_"):
                        clean_name = hero_name[14:]
                        # player_id 0-4 = radiant, 5-9 = dire
                        if hasattr(hero_snap, 'player_id'):
                            if hero_snap.player_id < 5:
                                radiant_heroes.add(clean_name)
                            else:
                                dire_heroes.add(clean_name)

            # Stop once we have all 10 heroes
            if len(radiant_heroes) == 5 and len(dire_heroes) == 5:
                break

        return radiant_heroes, dire_heroes

    def get_fight_combat_log(
        self,
        data: ParsedReplayData,
        reference_time: float,
        hero: Optional[str] = None,
        use_combat_detection: bool = True,
        detail_level: DetailLevel = DetailLevel.NARRATIVE,
        max_events: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Get fight boundaries, combat log, and highlights for a fight at a given time.

        Uses combat-intensity based detection by default to properly capture
        fight start (including BKB+Blink initiation) and fights without deaths.

        Args:
            data: ParsedReplayData from ReplayService
            reference_time: Game time to anchor the fight search
            hero: Optional hero name to anchor fight detection
            use_combat_detection: Use combat-based detection (default True)
            detail_level: Controls verbosity of returned events (NARRATIVE, TACTICAL, FULL)
            max_events: Maximum events to return (None = no limit)

        Returns:
            Dictionary with fight info, combat events, and highlights, or None if no fight found
        """
        # Get all combat events ONCE for detection, response, and highlights
        # This avoids iterating over the entire combat log 3 times
        all_events = self._combat.get_combat_log(
            data, detail_level=DetailLevel.FULL
        )
        deaths = self._combat.get_hero_deaths(data)

        if use_combat_detection:
            # Use combat-intensity based detection
            fight = self._detector.get_fight_at_time_from_combat(
                all_events, deaths, reference_time, hero
            )
        else:
            # Legacy death-based detection
            fight = self.get_fight_at_time(data, reference_time, hero)

        if not fight:
            return None

        # Get events within fight boundaries (with buffer)
        start_time = fight.start_time - 2.0
        end_time = fight.end_time + 2.0

        # Filter events from already-loaded all_events instead of re-iterating combat log
        # This is O(n) on the already-loaded list, not O(n) on raw combat log entries
        highlight_events = [
            e for e in all_events
            if start_time <= e.game_time <= end_time
        ]

        # Apply detail level filter for response events
        response_events = self._filter_events_by_detail_level(
            highlight_events, detail_level, max_events
        )

        # Get team rosters for ace detection
        radiant_heroes, dire_heroes = self._get_team_heroes(data)

        # Analyze fight for highlights
        highlights = self._analyzer.analyze_fight(
            events=highlight_events,
            deaths=fight.deaths,
            radiant_heroes=radiant_heroes,
            dire_heroes=dire_heroes,
        )

        return {
            "fight_id": fight.fight_id,
            "fight_start": fight.start_time,
            "fight_start_str": fight.start_time_str,
            "fight_end": fight.end_time,
            "fight_end_str": fight.end_time_str,
            "duration": fight.duration,
            "participants": fight.participants,
            "deaths": fight.deaths,
            "total_deaths": fight.total_deaths,
            "is_teamfight": fight.is_teamfight,
            "total_events": len(response_events),
            "events": response_events,
            "highlights": highlights,
            "detail_level": detail_level.value,
        }
