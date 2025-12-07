"""
Fight analyzer - extracts key highlights from teamfight combat logs.

Detects:
- Multi-hero abilities (Chronosphere catching 4, Black Hole on 3, etc.)
- Kill streaks (Double Kill, Triple Kill, Ultra Kill, Rampage)
- Team wipes (Ace)
- Fight initiation
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set

from ..models.combat_data import (
    CombatLogEvent,
    FightHighlights,
    HeroDeath,
    KillStreak,
    MultiHeroAbility,
    TeamWipe,
)

# Big teamfight abilities that matter when hitting multiple heroes
# Format: internal_name -> (display_name, min_heroes_for_highlight)
BIG_TEAMFIGHT_ABILITIES: Dict[str, tuple] = {
    # Stuns/Disables
    "faceless_void_chronosphere": ("Chronosphere", 2),
    "enigma_black_hole": ("Black Hole", 2),
    "magnataur_reverse_polarity": ("Reverse Polarity", 2),
    "tidehunter_ravage": ("Ravage", 2),
    "earthshaker_echo_slam": ("Echo Slam", 3),
    "treant_overgrowth": ("Overgrowth", 2),
    "warlock_rain_of_chaos": ("Chaotic Offering", 2),
    "elder_titan_earth_splitter": ("Earth Splitter", 2),
    "magnus_skewer": ("Skewer", 2),
    "dark_seer_wall_of_replica": ("Wall of Replica", 2),
    "phoenix_supernova": ("Supernova", 2),
    "disruptor_static_storm": ("Static Storm", 2),
    "keeper_of_the_light_will_o_wisp": ("Will-O-Wisp", 2),
    "winter_wyvern_winters_curse": ("Winter's Curse", 2),
    "jakiro_ice_path": ("Ice Path", 2),
    "puck_dream_coil": ("Dream Coil", 2),
    "sand_king_epicenter": ("Epicenter", 2),
    "sand_king_burrowstrike": ("Burrowstrike", 2),
    "slardar_slithereen_crush": ("Slithereen Crush", 2),
    "centaur_hoof_stomp": ("Hoof Stomp", 2),
    "axe_berserkers_call": ("Berserker's Call", 2),
    "mars_arena_of_blood": ("Arena of Blood", 2),
    "mars_gods_rebuke": ("God's Rebuke", 2),
    "legion_commander_overwhelming_odds": ("Overwhelming Odds", 3),
    "void_spirit_resonant_pulse": ("Resonant Pulse", 2),
    "primal_beast_pulverize": ("Pulverize", 2),
    "primal_beast_onslaught": ("Onslaught", 2),

    # Big damage ultimates
    "crystal_maiden_freezing_field": ("Freezing Field", 2),
    "witch_doctor_death_ward": ("Death Ward", 2),
    "gyrocopter_call_down": ("Call Down", 2),
    "invoker_emp": ("EMP", 2),
    "invoker_chaos_meteor": ("Chaos Meteor", 2),
    "invoker_deafening_blast": ("Deafening Blast", 2),
    "kunkka_ghostship": ("Ghostship", 2),
    "kunkka_torrent_storm": ("Torrent Storm", 2),
    "leshrac_pulse_nova": ("Pulse Nova", 2),
    "lich_chain_frost": ("Chain Frost", 2),
    "lion_finger_of_death": ("Finger of Death", 2),  # Aghs multi-target
    "lina_laguna_blade": ("Laguna Blade", 2),  # Aghs multi-target
    "luna_eclipse": ("Eclipse", 2),
    "medusa_stone_gaze": ("Stone Gaze", 2),
    "necrophos_reapers_scythe": ("Reaper's Scythe", 1),
    "pugna_life_drain": ("Life Drain", 1),
    "queen_of_pain_sonic_wave": ("Sonic Wave", 2),
    "shadow_fiend_requiem_of_souls": ("Requiem of Souls", 2),
    "skywrath_mage_mystic_flare": ("Mystic Flare", 1),
    "spectre_haunt": ("Haunt", 3),
    "storm_spirit_electric_vortex": ("Electric Vortex", 2),  # Aghs
    "techies_remote_mines": ("Remote Mines", 2),
    "tinker_march_of_the_machines": ("March of the Machines", 2),
    "venomancer_poison_nova": ("Poison Nova", 2),
    "zeus_thundergods_wrath": ("Thundergod's Wrath", 3),

    # Silences
    "death_prophet_silence": ("Silence", 2),
    "silencer_global_silence": ("Global Silence", 3),
    "drow_ranger_gust": ("Gust", 2),
    "night_stalker_crippling_fear": ("Crippling Fear", 2),

    # Saves (track single-target too)
    "dazzle_shallow_grave": ("Shallow Grave", 1),
    "oracle_false_promise": ("False Promise", 1),
    "abaddon_borrowed_time": ("Borrowed Time", 1),
    "omniknight_guardian_angel": ("Guardian Angel", 1),
}

# Modifiers that indicate ability hit (some abilities apply modifiers)
ABILITY_MODIFIERS: Dict[str, str] = {
    "modifier_faceless_void_chronosphere_freeze": "faceless_void_chronosphere",
    "modifier_enigma_black_hole_pull": "enigma_black_hole",
    "modifier_magnataur_reverse_polarity": "magnataur_reverse_polarity",
    "modifier_tidehunter_ravage": "tidehunter_ravage",
    "modifier_treant_overgrowth": "treant_overgrowth",
    "modifier_jakiro_ice_path_stun": "jakiro_ice_path",
    "modifier_puck_dream_coil": "puck_dream_coil",
    "modifier_sand_king_epicenter_slow": "sand_king_epicenter",
    "modifier_axe_berserkers_call": "axe_berserkers_call",
    "modifier_mars_arena_of_blood_leash": "mars_arena_of_blood",
    "modifier_disruptor_static_storm": "disruptor_static_storm",
    "modifier_medusa_stone_gaze_stone": "medusa_stone_gaze",
    "modifier_winter_wyvern_winters_curse": "winter_wyvern_winters_curse",
    "modifier_silencer_global_silence": "silencer_global_silence",
}

# Kill streak thresholds (Dota 2 uses 18 second window)
KILL_STREAK_WINDOW = 18.0
KILL_STREAK_TYPES = {
    2: "double_kill",
    3: "triple_kill",
    4: "ultra_kill",
    5: "rampage",
}


class FightAnalyzer:
    """Analyzes fight combat logs to extract key highlights."""

    def __init__(self):
        pass

    def _format_time(self, seconds: float) -> str:
        """Format game time as M:SS."""
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes}:{secs:02d}"

    def _clean_hero_name(self, name: str) -> str:
        """Remove npc_dota_hero_ prefix."""
        if name and name.startswith("npc_dota_hero_"):
            return name[14:]
        return name or ""

    def _clean_ability_name(self, name: str) -> str:
        """Clean ability name for matching."""
        if not name:
            return ""
        # Remove item_ prefix
        if name.startswith("item_"):
            return name
        return name

    def analyze_fight(
        self,
        events: List[CombatLogEvent],
        deaths: List[HeroDeath],
        radiant_heroes: Optional[Set[str]] = None,
        dire_heroes: Optional[Set[str]] = None,
    ) -> FightHighlights:
        """
        Analyze fight events and extract highlights.

        Args:
            events: Combat log events from the fight
            deaths: Hero deaths in the fight
            radiant_heroes: Set of radiant hero names (for team wipe detection)
            dire_heroes: Set of dire hero names (for team wipe detection)

        Returns:
            FightHighlights with key moments
        """
        highlights = FightHighlights()

        # Detect multi-hero abilities
        highlights.multi_hero_abilities = self._detect_multi_hero_abilities(events)

        # Detect kill streaks
        highlights.kill_streaks = self._detect_kill_streaks(deaths)

        # Detect team wipes
        if radiant_heroes and dire_heroes:
            highlights.team_wipes = self._detect_team_wipes(
                deaths, radiant_heroes, dire_heroes
            )

        # Detect fight initiation
        initiator, init_ability = self._detect_initiation(events, deaths)
        highlights.fight_initiator = initiator
        highlights.initiation_ability = init_ability

        return highlights

    def _detect_multi_hero_abilities(
        self, events: List[CombatLogEvent]
    ) -> List[MultiHeroAbility]:
        """
        Detect abilities that hit multiple heroes.

        Groups MODIFIER_ADD and ABILITY events by ability within 0.5s window.
        """
        multi_hits: List[MultiHeroAbility] = []

        # Group events by ability within time windows
        # Key: (ability, window_start) -> {targets, caster, first_time}
        ability_windows: Dict[str, Dict] = defaultdict(
            lambda: {"targets": set(), "caster": None, "time": None}
        )

        for event in events:
            ability = self._clean_ability_name(event.ability)
            if not ability:
                continue

            # Check if it's a tracked ability
            tracked_ability = None
            if ability in BIG_TEAMFIGHT_ABILITIES:
                tracked_ability = ability
            elif event.type == "MODIFIER_ADD":
                # Check if modifier maps to a tracked ability
                modifier_name = ability
                if modifier_name in ABILITY_MODIFIERS:
                    tracked_ability = ABILITY_MODIFIERS[modifier_name]

            if not tracked_ability:
                continue

            # Only count if target is a hero
            if not event.target_is_hero:
                continue

            target = self._clean_hero_name(event.target)
            caster = self._clean_hero_name(event.attacker)

            # Create window key (round to 0.5s windows)
            window_key = f"{tracked_ability}_{int(event.game_time * 2)}"

            window = ability_windows[window_key]
            window["targets"].add(target)
            if window["caster"] is None:
                window["caster"] = caster
                window["time"] = event.game_time
                window["ability"] = tracked_ability

        # Convert windows to MultiHeroAbility
        for window_data in ability_windows.values():
            window_ability: str = window_data.get("ability", "")
            if not window_ability:
                continue

            display_name, min_heroes = BIG_TEAMFIGHT_ABILITIES.get(
                window_ability, (window_ability, 2)
            )
            targets = list(window_data["targets"])
            hero_count = len(targets)

            if hero_count >= min_heroes:
                multi_hits.append(
                    MultiHeroAbility(
                        game_time=window_data["time"],
                        game_time_str=self._format_time(window_data["time"]),
                        ability=window_ability,
                        ability_display=display_name,
                        caster=window_data["caster"],
                        targets=sorted(targets),
                        hero_count=hero_count,
                    )
                )

        # Sort by time
        multi_hits.sort(key=lambda x: x.game_time)
        return multi_hits

    def _detect_kill_streaks(self, deaths: List[HeroDeath]) -> List[KillStreak]:
        """
        Detect kill streaks (double kill, rampage, etc.).

        Uses 18 second window per Dota 2 rules.
        """
        streaks: List[KillStreak] = []

        # Group deaths by killer
        kills_by_hero: Dict[str, List[HeroDeath]] = defaultdict(list)
        for death in deaths:
            if death.killer_is_hero:
                killer = self._clean_hero_name(death.killer)
                kills_by_hero[killer].append(death)

        # Find streaks for each hero
        for hero, kills in kills_by_hero.items():
            if len(kills) < 2:
                continue

            # Sort kills by time
            kills = sorted(kills, key=lambda d: d.game_time)

            # Sliding window to find streaks
            streak_start = 0
            for i in range(1, len(kills)):
                # Check if this kill is within 18s of streak start
                if kills[i].game_time - kills[streak_start].game_time > KILL_STREAK_WINDOW:
                    # End current streak, check if it's notable
                    streak_count = i - streak_start
                    if streak_count >= 2:
                        streak_kills = kills[streak_start:i]
                        self._add_streak_if_notable(streaks, hero, streak_kills)
                    streak_start = i

            # Check final streak
            streak_count = len(kills) - streak_start
            if streak_count >= 2:
                streak_kills = kills[streak_start:]
                self._add_streak_if_notable(streaks, hero, streak_kills)

        # Sort by time
        streaks.sort(key=lambda x: x.game_time)
        return streaks

    def _add_streak_if_notable(
        self,
        streaks: List[KillStreak],
        hero: str,
        kills: List[HeroDeath],
    ):
        """Add streak if it's double kill or better."""
        kill_count = len(kills)
        if kill_count < 2:
            return

        # Cap at rampage (5)
        streak_type = KILL_STREAK_TYPES.get(
            min(kill_count, 5),
            "rampage" if kill_count >= 5 else None,
        )
        if not streak_type:
            return

        last_kill = kills[-1]
        victims = [self._clean_hero_name(k.victim) for k in kills]

        streaks.append(
            KillStreak(
                game_time=last_kill.game_time,
                game_time_str=self._format_time(last_kill.game_time),
                hero=hero,
                streak_type=streak_type,
                kills=kill_count,
                victims=victims,
            )
        )

    def _detect_team_wipes(
        self,
        deaths: List[HeroDeath],
        radiant_heroes: Set[str],
        dire_heroes: Set[str],
    ) -> List[TeamWipe]:
        """
        Detect team wipes (all 5 heroes of one team dead).

        Checks if all 5 heroes of a team die within the fight.
        """
        wipes: List[TeamWipe] = []

        # Track deaths by team
        radiant_deaths = []
        dire_deaths = []

        for death in deaths:
            victim = self._clean_hero_name(death.victim)
            if victim in radiant_heroes:
                radiant_deaths.append(death)
            elif victim in dire_heroes:
                dire_deaths.append(death)

        # Check for radiant team wipe
        if len(set(self._clean_hero_name(d.victim) for d in radiant_deaths)) >= 5:
            radiant_deaths_sorted = sorted(radiant_deaths, key=lambda d: d.game_time)
            unique_victims = set()
            first_death = None
            last_death = None
            for d in radiant_deaths_sorted:
                v = self._clean_hero_name(d.victim)
                if v not in unique_victims:
                    unique_victims.add(v)
                    if first_death is None:
                        first_death = d
                    last_death = d
                if len(unique_victims) >= 5:
                    break

            if len(unique_victims) >= 5 and first_death and last_death:
                wipes.append(
                    TeamWipe(
                        game_time=last_death.game_time,
                        game_time_str=self._format_time(last_death.game_time),
                        team_wiped="radiant",
                        duration=last_death.game_time - first_death.game_time,
                        killer_team="dire",
                    )
                )

        # Check for dire team wipe
        if len(set(self._clean_hero_name(d.victim) for d in dire_deaths)) >= 5:
            dire_deaths_sorted = sorted(dire_deaths, key=lambda d: d.game_time)
            unique_victims = set()
            first_death = None
            last_death = None
            for d in dire_deaths_sorted:
                v = self._clean_hero_name(d.victim)
                if v not in unique_victims:
                    unique_victims.add(v)
                    if first_death is None:
                        first_death = d
                    last_death = d
                if len(unique_victims) >= 5:
                    break

            if len(unique_victims) >= 5 and first_death and last_death:
                wipes.append(
                    TeamWipe(
                        game_time=last_death.game_time,
                        game_time_str=self._format_time(last_death.game_time),
                        team_wiped="dire",
                        duration=last_death.game_time - first_death.game_time,
                        killer_team="radiant",
                    )
                )

        return wipes

    def _detect_initiation(
        self,
        events: List[CombatLogEvent],
        deaths: List[HeroDeath],
    ) -> tuple:
        """
        Detect who initiated the fight and with what ability.

        Looks for the first big AoE disable/damage ability.
        """
        if not events:
            return None, None

        # Sort events by time
        sorted_events = sorted(events, key=lambda e: e.game_time)

        # Look for first big ability that hit a hero
        for event in sorted_events:
            if event.type not in ("ABILITY", "MODIFIER_ADD"):
                continue

            ability = self._clean_ability_name(event.ability)
            if not ability:
                continue

            # Check if it's a tracked initiation ability
            if ability in BIG_TEAMFIGHT_ABILITIES:
                if event.target_is_hero:
                    caster = self._clean_hero_name(event.attacker)
                    display_name, _ = BIG_TEAMFIGHT_ABILITIES[ability]
                    return caster, display_name

            # Check modifier
            if ability in ABILITY_MODIFIERS:
                mapped_ability = ABILITY_MODIFIERS[ability]
                if mapped_ability in BIG_TEAMFIGHT_ABILITIES and event.target_is_hero:
                    caster = self._clean_hero_name(event.attacker)
                    display_name, _ = BIG_TEAMFIGHT_ABILITIES[mapped_ability]
                    return caster, display_name

        return None, None
