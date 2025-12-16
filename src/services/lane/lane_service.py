"""
Lane service for laning phase analysis.

Tracks last hits, denies, harass, tower proximity, rotations, and wave nuking.
NO MCP DEPENDENCIES.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from python_manta import CombatLogType

from ..models.lane_data import (
    CreepWave,
    HeroLanePhase,
    HeroPosition,
    LaneHarass,
    LaneLastHit,
    LaneRotation,
    LaneSummaryResponse,
    NeutralAggro,
    TowerPressure,
    TowerProximityEvent,
    WaveNuke,
)
from ..models.replay_data import ParsedReplayData

# Type alias for contested CS data
ContestedCS = Dict[str, Any]

logger = logging.getLogger(__name__)

LANE_BOUNDARIES = {
    "top": {"x_min": -7000, "x_max": 0, "y_min": 2000, "y_max": 8000},
    "mid": {"x_min": -3000, "x_max": 3000, "y_min": -3000, "y_max": 3000},
    "bot": {"x_min": 0, "x_max": 7000, "y_min": -8000, "y_max": -2000},
}

LANING_PHASE_END = 600  # 10 minutes


class LaneService:
    """
    Service for lane analysis.

    Provides:
    - Hero last hits and denies with positions
    - Harass/trading detection
    - Tower proximity timeline
    - Rotation detection (smoke, TP, twin gate)
    - Wave nuke detection
    """

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

    def _classify_lane(self, x: float, y: float) -> str:
        """Classify position to a lane."""
        for lane, bounds in LANE_BOUNDARIES.items():
            if (bounds["x_min"] <= x <= bounds["x_max"] and
                bounds["y_min"] <= y <= bounds["y_max"]):
                return lane
        return "jungle"

    def _get_hero_position_at_time(
        self,
        data: ParsedReplayData,
        hero: str,
        target_time: float,
    ) -> Tuple[Optional[float], Optional[float], str]:
        """Get hero position at a specific time."""
        hero_lower = hero.lower()
        best_snapshot = None
        min_diff = float('inf')

        for snapshot in data.entity_snapshots:
            diff = abs(snapshot.game_time - target_time)
            if diff < min_diff:
                min_diff = diff
                best_snapshot = snapshot

        if not best_snapshot or min_diff > 30.0:
            return (None, None, "unknown")

        for hero_snap in best_snapshot.heroes:
            hero_name = self._clean_hero_name(hero_snap.hero_name)
            if hero_lower in hero_name.lower():
                lane = self._classify_lane(hero_snap.x, hero_snap.y)
                return (hero_snap.x, hero_snap.y, lane)

        return (None, None, "unknown")

    def _is_lane_creep(self, name: str) -> bool:
        """Check if target is a lane creep."""
        name_lower = name.lower()
        return ("creep" in name_lower and
                ("lane" in name_lower or "melee" in name_lower or "ranged" in name_lower or
                 "badguys" in name_lower or "goodguys" in name_lower) and
                "neutral" not in name_lower)

    def _is_deny(self, attacker_team: int, target_name: str) -> bool:
        """Check if this was a deny (killing own team's creep)."""
        target_lower = target_name.lower()
        is_radiant_creep = "goodguys" in target_lower
        attacker_is_radiant = attacker_team == 2  # Team.RADIANT.value
        return is_radiant_creep == attacker_is_radiant

    def get_lane_last_hits(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[LaneLastHit]:
        """
        Get all last hit and deny events during laning phase.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include CS by this hero
            end_time: End of laning phase (default 10:00)

        Returns:
            List of LaneLastHit events sorted by game time
        """
        last_hits = []
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type
            if entry_type != CombatLogType.DEATH.value:
                continue

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            if not entry.is_attacker_hero:
                continue

            if not self._is_lane_creep(entry.target_name):
                continue

            hero = self._clean_hero_name(entry.attacker_name)
            if hero_filter_lower and hero_filter_lower not in hero.lower():
                continue

            pos_x, pos_y, lane = self._get_hero_position_at_time(data, hero, entry.game_time)
            is_deny = self._is_deny(entry.attacker_team, entry.target_name)

            last_hits.append(LaneLastHit(
                game_time=entry.game_time,
                game_time_str=self._format_time(entry.game_time),
                hero=hero,
                target=entry.target_name,
                is_deny=is_deny,
                position_x=pos_x,
                position_y=pos_y,
                lane=lane,
            ))

        return sorted(last_hits, key=lambda x: x.game_time)

    def get_lane_harass(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[LaneHarass]:
        """
        Get hero-to-hero damage events during laning phase.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include harass involving this hero
            end_time: End of laning phase (default 10:00)

        Returns:
            List of LaneHarass events sorted by game time
        """
        harass_events = []
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type
            if entry_type != CombatLogType.DAMAGE.value:
                continue

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            if not entry.is_attacker_hero or not entry.is_target_hero:
                continue

            attacker = self._clean_hero_name(entry.attacker_name)
            target = self._clean_hero_name(entry.target_name)

            if hero_filter_lower:
                if hero_filter_lower not in attacker.lower() and hero_filter_lower not in target.lower():
                    continue

            pos_x, pos_y, lane = self._get_hero_position_at_time(data, attacker, entry.game_time)

            ability = entry.inflictor_name
            if ability == "dota_unknown":
                ability = None

            harass_events.append(LaneHarass(
                game_time=entry.game_time,
                game_time_str=self._format_time(entry.game_time),
                attacker=attacker,
                target=target,
                damage=entry.value or 0,
                ability=ability,
                lane=lane,
            ))

        return sorted(harass_events, key=lambda x: x.game_time)

    def get_tower_proximity_timeline(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[TowerProximityEvent]:
        """
        Get timeline of when heroes enter/leave tower range.

        Uses modifier_tower_aura_bonus to detect tower proximity.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include events for this hero
            end_time: End of laning phase (default 10:00)

        Returns:
            List of TowerProximityEvent sorted by game time
        """
        events = []
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type

            if entry_type not in (CombatLogType.MODIFIER_ADD.value, CombatLogType.MODIFIER_REMOVE.value):
                continue

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            inflictor = getattr(entry, 'inflictor_name', '') or ''
            if 'modifier_tower_aura_bonus' not in inflictor:
                continue

            if not entry.is_target_hero:
                continue

            hero = self._clean_hero_name(entry.target_name)
            if hero_filter_lower and hero_filter_lower not in hero.lower():
                continue

            # Determine tower team from target team (tower aura applies to allied heroes)
            tower_team = "radiant" if entry.target_team == 2 else "dire"
            event_type = "entered" if entry_type == CombatLogType.MODIFIER_ADD.value else "left"

            events.append(TowerProximityEvent(
                game_time=entry.game_time,
                game_time_str=self._format_time(entry.game_time),
                hero=hero,
                tower_team=tower_team,
                event_type=event_type,
            ))

        return sorted(events, key=lambda x: x.game_time)

    def get_wave_nukes(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
        min_creeps_hit: int = 2,
        time_window: float = 1.0,
    ) -> List[WaveNuke]:
        """
        Detect when heroes use abilities to damage multiple lane creeps.

        Groups damage events within a time window to detect AoE wave clearing.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include nukes by this hero
            end_time: End of laning phase (default 10:00)
            min_creeps_hit: Minimum creeps to count as wave nuke (default 2)
            time_window: Seconds to group damage events (default 1.0)

        Returns:
            List of WaveNuke events sorted by game time
        """
        # Collect all ability damage to lane creeps
        ability_damage: Dict[str, List[dict]] = defaultdict(list)
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type
            if entry_type != CombatLogType.DAMAGE.value:
                continue

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            if not entry.is_attacker_hero:
                continue

            if not self._is_lane_creep(entry.target_name):
                continue

            ability = entry.inflictor_name
            if not ability or ability == "dota_unknown":
                continue  # Skip right-click damage

            hero = self._clean_hero_name(entry.attacker_name)
            if hero_filter_lower and hero_filter_lower not in hero.lower():
                continue

            key = f"{hero}:{ability}:{int(entry.game_time / time_window)}"
            ability_damage[key].append({
                "game_time": entry.game_time,
                "hero": hero,
                "ability": ability,
                "target": entry.target_name,
                "damage": entry.value or 0,
            })

        # Convert grouped damage to WaveNuke events
        wave_nukes = []
        for key, damages in ability_damage.items():
            if len(damages) < min_creeps_hit:
                continue

            first = damages[0]
            total_damage = sum(d["damage"] for d in damages)
            creeps_hit = len(set(d["target"] for d in damages))

            if creeps_hit < min_creeps_hit:
                continue

            pos_x, pos_y, lane = self._get_hero_position_at_time(data, first["hero"], first["game_time"])

            wave_nukes.append(WaveNuke(
                game_time=first["game_time"],
                game_time_str=self._format_time(first["game_time"]),
                hero=first["hero"],
                ability=first["ability"],
                creeps_hit=creeps_hit,
                total_damage=total_damage,
                lane=lane,
            ))

        return sorted(wave_nukes, key=lambda x: x.game_time)

    def get_lane_rotations(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[LaneRotation]:
        """
        Detect rotation events: smoke breaks, TP scrolls, twin gate usage.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include rotations by this hero
            end_time: End of laning phase (default 10:00)

        Returns:
            List of LaneRotation events sorted by game time
        """
        rotations = []
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        # Track modifiers that indicate rotation
        rotation_modifiers = {
            "modifier_smoke_of_deceit": "smoke_break",
            "modifier_teleporting": "tp_scroll",
            "modifier_twin_gate_warp_channel": "twin_gate",
        }

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            # Check for smoke break (MODIFIER_REMOVE of smoke)
            if entry_type == CombatLogType.MODIFIER_REMOVE.value:
                inflictor = getattr(entry, 'inflictor_name', '') or ''
                if 'modifier_smoke_of_deceit' in inflictor and entry.is_target_hero:
                    hero = self._clean_hero_name(entry.target_name)
                    if hero_filter_lower and hero_filter_lower not in hero.lower():
                        continue

                    pos_x, pos_y, lane = self._get_hero_position_at_time(data, hero, entry.game_time)

                    rotations.append(LaneRotation(
                        game_time=entry.game_time,
                        game_time_str=self._format_time(entry.game_time),
                        hero=hero,
                        rotation_type="smoke_break",
                        from_position_x=pos_x,
                        from_position_y=pos_y,
                        to_lane=lane,
                    ))

            # Check for TP or twin gate (MODIFIER_ADD)
            elif entry_type == CombatLogType.MODIFIER_ADD.value:
                inflictor = getattr(entry, 'inflictor_name', '') or ''

                for modifier_name, rotation_type in rotation_modifiers.items():
                    if modifier_name == "modifier_smoke_of_deceit":
                        continue  # Handle smoke separately on removal

                    if modifier_name in inflictor and entry.is_target_hero:
                        hero = self._clean_hero_name(entry.target_name)
                        if hero_filter_lower and hero_filter_lower not in hero.lower():
                            continue

                        pos_x, pos_y, _ = self._get_hero_position_at_time(data, hero, entry.game_time)

                        rotations.append(LaneRotation(
                            game_time=entry.game_time,
                            game_time_str=self._format_time(entry.game_time),
                            hero=hero,
                            rotation_type=rotation_type,
                            from_position_x=pos_x,
                            from_position_y=pos_y,
                            to_lane=None,  # Destination determined later
                        ))
                        break

        return sorted(rotations, key=lambda x: x.game_time)

    def _get_neutral_camp_type(self, camp_type_value: Optional[int]) -> Optional[str]:
        """Convert neutral_camp_type value to string."""
        if camp_type_value is None:
            return None
        camp_map = {0: "small", 1: "medium", 2: "large", 3: "ancient"}
        return camp_map.get(camp_type_value)

    def _is_neutral_creep(self, name: str) -> bool:
        """Check if target is a neutral creep."""
        return bool(name) and "neutral" in name.lower()

    def _is_tower(self, name: str) -> bool:
        """Check if attacker is a tower."""
        name_lower = name.lower()
        return "tower" in name_lower and ("goodguys" in name_lower or "badguys" in name_lower)

    def _get_tower_lane(self, tower_name: str) -> str:
        """Extract lane from tower name."""
        name_lower = tower_name.lower()
        if "top" in name_lower:
            return "top"
        elif "mid" in name_lower:
            return "mid"
        elif "bot" in name_lower:
            return "bot"
        return "unknown"

    def _get_tower_team(self, tower_name: str) -> str:
        """Extract team from tower name."""
        return "radiant" if "goodguys" in tower_name.lower() else "dire"

    def _get_nearest_lane(self, x: Optional[float], y: Optional[float]) -> Optional[str]:
        """Determine nearest lane based on position."""
        if x is None or y is None:
            return None
        # Check standard lane boundaries
        lane = self._classify_lane(x, y)
        if lane != "jungle":
            return lane
        # For jungle positions, estimate nearest lane
        if x < -2000:
            return "top" if y > 0 else "bot"
        elif x > 2000:
            return "bot" if y < 0 else "top"
        return "mid"

    def get_neutral_aggro(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[NeutralAggro]:
        """
        Get hero attacks on neutral creeps during laning phase.

        Useful for detecting pull attempts and aggro manipulation.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include attacks by this hero
            end_time: End of laning phase (default 10:00)

        Returns:
            List of NeutralAggro events sorted by game time
        """
        aggro_events = []
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type
            if entry_type != CombatLogType.DAMAGE.value:
                continue

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            if not entry.is_attacker_hero:
                continue

            if not self._is_neutral_creep(entry.target_name):
                continue

            hero = self._clean_hero_name(entry.attacker_name)
            if hero_filter_lower and hero_filter_lower not in hero.lower():
                continue

            pos_x, pos_y, _ = self._get_hero_position_at_time(data, hero, entry.game_time)
            near_lane = self._get_nearest_lane(pos_x, pos_y)
            camp_type = self._get_neutral_camp_type(
                getattr(entry, 'neutral_camp_type', None)
            )

            aggro_events.append(NeutralAggro(
                game_time=entry.game_time,
                game_time_str=self._format_time(entry.game_time),
                hero=hero,
                target=entry.target_name,
                damage=entry.value or 0,
                camp_type=camp_type,
                position_x=pos_x,
                position_y=pos_y,
                near_lane=near_lane,
            ))

        return sorted(aggro_events, key=lambda x: x.game_time)

    def get_tower_pressure(
        self,
        data: ParsedReplayData,
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[TowerPressure]:
        """
        Get tower attacks on heroes during laning phase.

        Tracks when heroes take tower aggro/damage.

        Args:
            data: ParsedReplayData from ReplayService
            hero_filter: Only include damage to this hero
            end_time: End of laning phase (default 10:00)

        Returns:
            List of TowerPressure events sorted by game time
        """
        pressure_events = []
        hero_filter_lower = hero_filter.lower() if hero_filter else None

        for entry in data.combat_log_entries:
            entry_type = entry.type.value if hasattr(entry.type, 'value') else entry.type
            if entry_type != CombatLogType.DAMAGE.value:
                continue

            if entry.game_time < 0 or entry.game_time > end_time:
                continue

            if not self._is_tower(entry.attacker_name):
                continue

            if not entry.is_target_hero:
                continue

            hero = self._clean_hero_name(entry.target_name)
            if hero_filter_lower and hero_filter_lower not in hero.lower():
                continue

            tower_team = self._get_tower_team(entry.attacker_name)
            tower_lane = self._get_tower_lane(entry.attacker_name)

            pressure_events.append(TowerPressure(
                game_time=entry.game_time,
                game_time_str=self._format_time(entry.game_time),
                tower=entry.attacker_name,
                hero=hero,
                damage=entry.value or 0,
                tower_team=tower_team,
                lane=tower_lane,
            ))

        return sorted(pressure_events, key=lambda x: x.game_time)

    def get_hero_positions_at_minute(
        self,
        data: ParsedReplayData,
        minute: int,
    ) -> List[HeroPosition]:
        """Get hero positions at a specific minute."""
        target_time = minute * 60
        positions = []

        best_snapshot = None
        min_diff = float('inf')

        for snapshot in data.entity_snapshots:
            diff = abs(snapshot.game_time - target_time)
            if diff < min_diff:
                min_diff = diff
                best_snapshot = snapshot

        if not best_snapshot:
            return positions

        for hero_snap in best_snapshot.heroes:
            hero_name = self._clean_hero_name(hero_snap.hero_name)
            if not hero_name:
                continue

            team = 'radiant' if hero_snap.player_id < 5 else 'dire'

            positions.append(HeroPosition(
                game_time=best_snapshot.game_time,
                tick=best_snapshot.tick,
                hero=hero_name,
                x=hero_snap.x,
                y=hero_snap.y,
                team=team,
            ))

        return positions

    def get_cs_at_minute(
        self,
        data: ParsedReplayData,
        minute: int,
    ) -> Dict[str, Dict[str, int]]:
        """Get last hits, denies, gold, level for all heroes at a specific minute."""
        target_time = minute * 60
        cs_data = {}

        best_snapshot = None
        min_diff = float('inf')

        for snapshot in data.entity_snapshots:
            diff = abs(snapshot.game_time - target_time)
            if diff < min_diff:
                min_diff = diff
                best_snapshot = snapshot

        if not best_snapshot:
            return cs_data

        for hero_snap in best_snapshot.heroes:
            hero_name = self._clean_hero_name(hero_snap.hero_name)
            if not hero_name:
                continue

            cs_data[hero_name] = {
                'last_hits': hero_snap.last_hits,
                'denies': hero_snap.denies,
                'gold': hero_snap.gold,
                'level': hero_snap.level,
            }

        return cs_data

    def get_lane_summary(
        self,
        data: ParsedReplayData,
        match_id: int = 0,
    ) -> LaneSummaryResponse:
        """
        Get complete laning phase summary with all tracked events.

        Args:
            data: ParsedReplayData from ReplayService
            match_id: Match ID for response

        Returns:
            LaneSummaryResponse with comprehensive lane data
        """
        cs_5min = self.get_cs_at_minute(data, 5)
        cs_10min = self.get_cs_at_minute(data, 10)
        positions_5min = self.get_hero_positions_at_minute(data, 5)

        all_last_hits = self.get_lane_last_hits(data)
        all_harass = self.get_lane_harass(data)
        tower_events = self.get_tower_proximity_timeline(data)
        wave_nukes = self.get_wave_nukes(data)
        rotations = self.get_lane_rotations(data)
        all_neutral_aggro = self.get_neutral_aggro(data)
        all_tower_pressure = self.get_tower_pressure(data)

        # Build hero stats
        hero_stats = []
        for pos in positions_5min:
            lane = self._classify_lane(pos.x, pos.y)
            if lane == "jungle":
                lane = "roaming"

            if pos.team == 'radiant':
                if lane == 'bot':
                    role = 'core'
                elif lane == 'top':
                    role = 'offlane'
                else:
                    role = 'mid' if lane == 'mid' else 'support'
            else:
                if lane == 'top':
                    role = 'core'
                elif lane == 'bot':
                    role = 'offlane'
                else:
                    role = 'mid' if lane == 'mid' else 'support'

            stats_5 = cs_5min.get(pos.hero, {})
            stats_10 = cs_10min.get(pos.hero, {})

            # Filter events for this hero
            hero_last_hits = [lh for lh in all_last_hits if lh.hero == pos.hero]
            hero_harass_dealt = [h for h in all_harass if h.attacker == pos.hero]
            hero_harass_received = [h for h in all_harass if h.target == pos.hero]

            damage_dealt = sum(h.damage for h in hero_harass_dealt)
            damage_received = sum(h.damage for h in hero_harass_received)

            # Calculate tower proximity time
            hero_tower_events = [t for t in tower_events if t.hero == pos.hero]
            own_tower_time = 0.0
            enemy_tower_time = 0.0
            current_own_start = None
            current_enemy_start = None

            for event in hero_tower_events:
                is_own_tower = event.tower_team == pos.team
                if event.event_type == "entered":
                    if is_own_tower:
                        current_own_start = event.game_time
                    else:
                        current_enemy_start = event.game_time
                else:
                    if is_own_tower and current_own_start:
                        own_tower_time += event.game_time - current_own_start
                        current_own_start = None
                    elif not is_own_tower and current_enemy_start:
                        enemy_tower_time += event.game_time - current_enemy_start
                        current_enemy_start = None

            # Neutral aggro stats
            hero_neutral_aggro = [na for na in all_neutral_aggro if na.hero == pos.hero]
            neutral_attacks_count = len(hero_neutral_aggro)
            # Estimate pull attempts: aggro events where hero is near a lane (not deep jungle)
            pull_attempts = sum(1 for na in hero_neutral_aggro if na.near_lane in ['top', 'bot', 'mid'])

            # Tower pressure stats (from enemy towers)
            hero_tower_pressure = [tp for tp in all_tower_pressure
                                   if tp.hero == pos.hero and tp.tower_team != pos.team]
            tower_damage = sum(tp.damage for tp in hero_tower_pressure)
            tower_hits = len(hero_tower_pressure)

            hero_stats.append(HeroLanePhase(
                hero=pos.hero,
                team=pos.team,
                lane=lane,
                role=role,
                last_hits_5min=stats_5.get('last_hits', 0),
                last_hits_10min=stats_10.get('last_hits', 0),
                denies_5min=stats_5.get('denies', 0),
                denies_10min=stats_10.get('denies', 0),
                gold_5min=stats_5.get('gold', 0),
                gold_10min=stats_10.get('gold', 0),
                level_5min=stats_5.get('level', 1),
                level_10min=stats_10.get('level', 1),
                damage_dealt_to_heroes=damage_dealt,
                damage_received_from_heroes=damage_received,
                time_under_own_tower=own_tower_time,
                time_under_enemy_tower=enemy_tower_time,
                neutral_attacks=neutral_attacks_count,
                pull_attempts=pull_attempts,
                tower_damage_taken=tower_damage,
                tower_hits_received=tower_hits,
                last_hit_events=hero_last_hits,
                harass_events=hero_harass_dealt,
                neutral_aggro_events=hero_neutral_aggro,
                tower_pressure_events=hero_tower_pressure,
            ))

        # Determine lane winners
        lane_winners = self._determine_lane_winners(hero_stats)

        radiant_score = sum(
            s.last_hits_10min + s.denies_10min * 0.5
            for s in hero_stats if s.team == 'radiant'
        )
        dire_score = sum(
            s.last_hits_10min + s.denies_10min * 0.5
            for s in hero_stats if s.team == 'dire'
        )

        return LaneSummaryResponse(
            success=True,
            match_id=match_id,
            top_winner=lane_winners.get('top'),
            mid_winner=lane_winners.get('mid'),
            bot_winner=lane_winners.get('bot'),
            radiant_laning_score=radiant_score,
            dire_laning_score=dire_score,
            hero_stats=hero_stats,
            rotations=rotations,
            wave_nukes=wave_nukes,
            neutral_aggro=all_neutral_aggro,
            tower_pressure=all_tower_pressure,
        )

    def _determine_lane_winners(
        self,
        hero_stats: List[HeroLanePhase],
    ) -> Dict[str, str]:
        """Determine winner of each lane based on CS."""
        lane_scores: Dict[str, Dict[str, int]] = {
            'top': {'radiant': 0, 'dire': 0},
            'mid': {'radiant': 0, 'dire': 0},
            'bot': {'radiant': 0, 'dire': 0},
        }

        for stats in hero_stats:
            if stats.lane in lane_scores:
                score = stats.last_hits_10min + stats.denies_10min
                lane_scores[stats.lane][stats.team] += score

        winners = {}
        for lane, scores in lane_scores.items():
            if scores['radiant'] > scores['dire']:
                winners[lane] = 'radiant'
            elif scores['dire'] > scores['radiant']:
                winners[lane] = 'dire'
            else:
                winners[lane] = 'even'

        return winners

    def _get_wave_number_for_time(self, death_time: float) -> int:
        """
        Determine which wave a creep death belongs to.

        Waves spawn every 30 seconds (0:00, 0:30, 1:00, ...).
        Creeps typically die 35-60 seconds after spawn depending on lane.
        Uses non-overlapping 30-second windows aligned with spawn times.
        """
        # Wave N spawns at (N-1)*30 seconds
        # Deaths typically occur 35-60 seconds after spawn
        # Use non-overlapping windows: spawn+35 to spawn+65 (30 second window)
        for wave_num in range(1, 21):  # Support up to wave 20 (10 min)
            spawn_time = (wave_num - 1) * 30
            death_window_start = spawn_time + 35  # Earliest typical death
            death_window_end = spawn_time + 65    # Latest typical death
            if death_window_start <= death_time < death_window_end:
                return wave_num
        return 0  # Unknown wave

    def get_lane_waves(
        self,
        data: ParsedReplayData,
        lane: str = "bot",
        team: str = "radiant",
        hero_filter: Optional[str] = None,
        end_time: float = LANING_PHASE_END,
    ) -> List[CreepWave]:
        """
        Get creep waves with CS breakdown using entity_deaths + combat_log.

        Uses entity_deaths collector to track ALL creep deaths with position
        for lane filtering, then uses combat_log to determine who got each last hit.

        Args:
            data: ParsedReplayData from ReplayService
            lane: Lane to analyze (top, mid, bot)
            team: Which team's creeps to track (radiant or dire)
            hero_filter: Only include CS from this hero
            end_time: End time for analysis

        Returns:
            List of CreepWave objects with CS grouped by wave

        Raises:
            ValueError: If entity_deaths data not available
        """
        creep_deaths = self._get_creep_deaths_from_entity_deaths(data, lane, team, end_time)
        if not creep_deaths:
            raise ValueError(
                "entity_deaths data not available. "
                "Requires python-manta 1.4.5.4+ and replay must be re-parsed."
            )

        # Build combat_log death index for last hit attribution
        # Combat_log has killer name directly - more reliable than attack correlation
        combat_log_deaths = self._build_combat_log_death_index(data, team, end_time)

        hero_filter_lower = hero_filter.lower() if hero_filter else None
        waves: Dict[int, CreepWave] = {}

        for death in creep_deaths:
            wave_num = self._get_wave_number_for_time(death['game_time'])
            if wave_num == 0:
                continue

            # Find who got the last hit via combat_log (match by time)
            last_hitter = self._find_killer_from_combat_log(
                death['game_time'], combat_log_deaths
            )

            # Create wave if not exists
            if wave_num not in waves:
                spawn_time = (wave_num - 1) * 30
                waves[wave_num] = CreepWave(
                    wave_number=wave_num,
                    spawn_time=spawn_time,
                    spawn_time_str=self._format_time(spawn_time),
                    lane=lane,
                    team=team,
                )

            wave = waves[wave_num]

            # Update wave death times
            if wave.first_death_time is None or death['game_time'] < wave.first_death_time:
                wave.first_death_time = death['game_time']
            if wave.last_death_time is None or death['game_time'] > wave.last_death_time:
                wave.last_death_time = death['game_time']

            # Count creep types
            if death['is_melee']:
                wave.melee_deaths += 1
            elif death['is_ranged']:
                wave.ranged_deaths += 1

            wave.total_deaths += 1

            # Add to last_hits if a hero got the CS (filtered if hero_filter set)
            if last_hitter and (not hero_filter_lower or hero_filter_lower in last_hitter.lower()):
                lh = LaneLastHit(
                    game_time=death['game_time'],
                    game_time_str=self._format_time(death['game_time']),
                    hero=last_hitter,
                    target=death['name'],
                    is_deny=False,  # TODO: detect denies via team comparison
                    position_x=None,
                    position_y=None,
                    lane=lane,
                    wave_number=wave_num,
                )
                wave.last_hits.append(lh)

        return sorted(waves.values(), key=lambda w: w.wave_number)

    def _build_hero_index(self, data: ParsedReplayData) -> Dict[int, str]:
        """
        Build index of entity_index → hero_name from entity snapshots.

        Used to identify which attacks came from heroes.

        Returns:
            Dict mapping entity_index to hero name (e.g., 1326 -> "centaur")
        """
        hero_index: Dict[int, str] = {}

        if not data.entity_snapshots:
            return hero_index

        # Find snapshot with all 10 heroes (early snapshots may have partial data)
        for snapshot in data.entity_snapshots:
            if not snapshot.heroes or len(snapshot.heroes) < 10:
                continue
            for hero_snap in snapshot.heroes:
                # HeroSnapshot uses 'index' field, not 'entity_index'
                entity_index = getattr(hero_snap, 'index', None) or getattr(hero_snap, 'entity_id', None)
                hero_name = getattr(hero_snap, 'hero_name', '')
                if entity_index and hero_name:
                    hero_index[entity_index] = self._clean_hero_name(hero_name)
            # Found complete snapshot
            if len(hero_index) == 10:
                break

        return hero_index

    def _build_attack_index(
        self,
        data: ParsedReplayData,
        end_time: float = LANING_PHASE_END,
    ) -> Dict[int, List[dict]]:
        """
        Build index of entity_id → attacks for correlation.

        Requires python-manta 1.4.5.4+ with attacks collector.
        With 1.4.5.4.dev4+, both melee and ranged attacks have:
        - source_index/target_index (entity IDs)
        - attacker_name/target_name (entity names)

        Returns:
            Dict mapping target entity_id (target_index) to list of attack events
        """
        if not data.attacks or not hasattr(data.attacks, 'events'):
            return {}

        attack_index: Dict[int, List[dict]] = defaultdict(list)

        for attack in data.attacks.events:
            if attack.game_time > end_time:
                continue

            target_id = getattr(attack, 'target_index', None)
            if target_id is None:
                continue

            source_id = getattr(attack, 'source_index', None)
            attacker_name = getattr(attack, 'attacker_name', '') or ''

            attack_index[target_id].append({
                'game_time': attack.game_time,
                'source_index': source_id,
                'target_id': target_id,
                'attacker_name': attacker_name,
            })

        return attack_index

    def _get_creep_deaths_from_entity_deaths(
        self,
        data: ParsedReplayData,
        lane: str,
        team: str,
        end_time: float = LANING_PHASE_END,
    ) -> List[dict]:
        """
        Extract lane creep deaths from entity_deaths collector.

        Requires python-manta 1.4.5.4+ with entity_deaths collector.

        Args:
            data: ParsedReplayData
            lane: Lane to filter ("bot", "top", "mid")
            team: Which team's creeps to track (for CS, this is the ENEMY team)
            end_time: End time for analysis

        Returns:
            List of creep death events with entity_id
        """
        if not data.entity_deaths or not hasattr(data.entity_deaths, 'events'):
            return []

        deaths = []

        for death in data.entity_deaths.events:
            if death.game_time > end_time:
                continue

            # Check if it's a lane creep using class_name (name is often empty)
            class_name = getattr(death, 'class_name', '') or ''
            if 'Creep_Lane' not in class_name:
                continue

            # Filter by lane position
            x, y = death.x, death.y
            if not self._position_matches_lane(x, y, lane):
                continue

            entity_id = getattr(death, 'entity_id', None)

            # Determine melee/ranged from max_health (melee=550, ranged=300)
            max_health = getattr(death, 'max_health', 0)
            is_melee = max_health >= 500
            is_ranged = max_health < 400 and max_health > 0

            deaths.append({
                'game_time': death.game_time,
                'entity_id': entity_id,
                'name': class_name,
                'is_melee': is_melee,
                'is_ranged': is_ranged,
                'x': x,
                'y': y,
            })

        return sorted(deaths, key=lambda d: d['game_time'])

    def _position_matches_lane(self, x: float, y: float, lane: str) -> bool:
        """Check if position matches the specified lane."""
        # Dota 2 map coordinates:
        # Bot lane: x > 10000, y < 6000 (bottom-right)
        # Top lane: x < 6000, y > 10000 (top-left)
        # Mid lane: diagonal, roughly 6000 < x < 10000, 6000 < y < 10000
        if lane == "bot":
            return x > 10000 and y < 6000
        elif lane == "top":
            return x < 6000 and y > 10000
        elif lane == "mid":
            return 6000 < x < 10000 and 6000 < y < 10000
        return True  # No filter if lane not specified

    def _build_combat_log_death_index(
        self,
        data: ParsedReplayData,
        team: str,
        end_time: float = LANING_PHASE_END,
    ) -> List[dict]:
        """
        Build index of lane creep deaths from combat_log.

        Combat_log DEATH events have the killer name directly,
        which is more reliable than attack correlation for melee heroes.

        Args:
            data: ParsedReplayData
            team: Which team's creeps (radiant=goodguys, dire=badguys)
            end_time: End time for analysis

        Returns:
            List of death events sorted by time with killer info
        """
        # Map team to creep name pattern
        creep_pattern = "creep_goodguys" if team == "radiant" else "creep_badguys"

        deaths = []
        for entry in data.combat_log_entries:
            if entry.type != CombatLogType.DEATH.value:
                continue
            if entry.game_time > end_time:
                continue

            target = entry.target_name or ""
            if creep_pattern not in target:
                continue

            killer = None
            if entry.is_attacker_hero:
                killer = self._clean_hero_name(entry.attacker_name)

            deaths.append({
                'game_time': entry.game_time,
                'target': target,
                'killer': killer,
                'is_hero_kill': entry.is_attacker_hero,
            })

        return sorted(deaths, key=lambda d: d['game_time'])

    def _find_killer_from_combat_log(
        self,
        death_time: float,
        combat_log_deaths: List[dict],
        tolerance: float = 1.0,
    ) -> Optional[str]:
        """
        Find who killed a creep by matching death time to combat_log.

        Args:
            death_time: Game time of the entity death
            combat_log_deaths: Pre-built index from _build_combat_log_death_index
            tolerance: Time tolerance for matching (seconds)

        Returns:
            Hero name if a hero got the last hit, None otherwise
        """
        for death in combat_log_deaths:
            if abs(death['game_time'] - death_time) <= tolerance:
                if death['is_hero_kill']:
                    return death['killer']
                return None  # Creep killed by non-hero
        return None  # No match found

    def get_contested_cs(
        self,
        data: ParsedReplayData,
        lane: str = "bot",
        team: str = "radiant",
        end_time: float = LANING_PHASE_END,
    ) -> List[ContestedCS]:
        """
        Detect contested CS - creeps attacked by multiple heroes.

        Uses entity_deaths + attacks correlation to find creeps
        where 2+ heroes competed for the last hit.

        Args:
            data: ParsedReplayData from ReplayService
            lane: Lane to analyze
            team: Which team's creeps (radiant or dire)
            end_time: End time for analysis

        Returns:
            List of contested CS events with attackers info

        Raises:
            ValueError: If entity_deaths or attacks data not available
        """
        creep_deaths = self._get_creep_deaths_from_entity_deaths(data, lane, team, end_time)
        if not creep_deaths:
            raise ValueError(
                "entity_deaths data not available. "
                "Requires python-manta 1.4.5.4+ and replay must be re-parsed."
            )

        attack_index = self._build_attack_index(data, end_time)
        if not attack_index:
            raise ValueError(
                "attacks data not available. "
                "Requires python-manta 1.4.5.4+ and replay must be re-parsed."
            )

        contested = []

        for death in creep_deaths:
            entity_id = death.get('entity_id')
            if entity_id is None:
                continue

            attacks = attack_index.get(entity_id, [])
            if not attacks:
                continue

            # Get unique hero attackers using attacker_name (available in dev4+)
            hero_attackers = list(set(
                self._clean_hero_name(a['attacker_name'])
                for a in attacks
                if a.get('attacker_name') and 'hero' in a['attacker_name'].lower()
            ))

            if len(hero_attackers) >= 2:
                # Find who got the last hit (last hero attack before death)
                hero_attacks_before_death = [
                    {'game_time': a['game_time'], 'hero': self._clean_hero_name(a['attacker_name'])}
                    for a in attacks
                    if a.get('attacker_name') and 'hero' in a['attacker_name'].lower()
                    and a['game_time'] <= death['game_time']
                ]
                hero_attacks_before_death.sort(key=lambda a: a['game_time'])

                last_hitter = hero_attacks_before_death[-1]['hero'] if hero_attacks_before_death else None

                wave_num = self._get_wave_number_for_time(death['game_time'])

                contested.append({
                    'game_time': death['game_time'],
                    'game_time_str': self._format_time(death['game_time']),
                    'entity_id': entity_id,
                    'creep_name': death['name'],
                    'wave_number': wave_num,
                    'hero_attackers': hero_attackers,
                    'last_hitter': last_hitter,
                    'total_attacks': len(attacks),
                    'hero_attacks': len(hero_attacks_before_death),
                })

        return sorted(contested, key=lambda c: c['game_time'])
