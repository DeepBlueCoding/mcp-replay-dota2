"""
Fight analyzer - extracts key highlights from teamfight combat logs.

Detects:
- Multi-hero abilities (Chronosphere catching 4, Black Hole on 3, etc.)
- Kill streaks (Double Kill, Triple Kill, Ultra Kill, Rampage)
- Team wipes (Ace)
- Fight initiation (BKB + Blink into big ability)
- Coordinated ultimates (2+ heroes ulting together)
- Refresher combos (double ultimates)
- Clutch saves (banish, Glimmer, Lotus on ally)
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from ..models.combat_data import (
    BKBBlinkCombo,
    ClutchSave,
    CombatLogEvent,
    CoordinatedUltimates,
    FightHighlights,
    GenericAoEHit,
    HeroDeath,
    KillStreak,
    MultiHeroAbility,
    RefresherCombo,
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
    "earthshaker_fissure": ("Fissure", 2),
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
    "nevermore_requiem": ("Requiem of Souls", 2),  # Replay uses old internal name
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
    "modifier_earthshaker_fissure_stun": "earthshaker_fissure",
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

# Generic AoE detection - ANY ability hitting this many heroes is notable
GENERIC_AOE_MIN_HEROES = 3

# Fast buyback threshold (seconds after death)
FAST_BUYBACK_THRESHOLD = 10.0

# BKB + Blink initiation window (seconds)
BKB_BLINK_WINDOW = 1.5  # BKB -> Blink -> Ability within this window

# Coordinated ultimates window (seconds)
COORDINATED_ULT_WINDOW = 3.0  # Two heroes ulting within this time = coordinated

# Blink items for initiation detection
BLINK_ITEMS = {
    "item_blink",
    "item_swift_blink",
    "item_arcane_blink",
    "item_overwhelming_blink",
}

# Save items/abilities - self-banish or immunity
SELF_SAVE_ITEMS = {
    "item_outworld_staff": "self_banish",  # OD staff - banish self
    "item_aeon_disk": "self_immunity",  # Aeon Disk proc
    "item_satanic": "self_heal",  # Satanic active
}

SELF_SAVE_ABILITIES = {
    "puck_phase_shift": "self_banish",
    "ember_spirit_sleight_of_fist": "self_invulnerable",
    "juggernaut_blade_fury": "self_magic_immune",
    "lifestealer_rage": "self_magic_immune",
    "slark_shadow_dance": "self_hidden",
    "storm_spirit_ball_lightning": "self_invulnerable",
    "void_spirit_dissimilate": "self_hidden",
    "faceless_void_time_walk": "self_invulnerable",
}

# Ally save items - cast on ally to save them
ALLY_SAVE_ITEMS = {
    "item_glimmer_cape": "ally_glimmer",
    "item_force_staff": "ally_force",
    "item_hurricane_pike": "ally_force",
    "item_lotus_orb": "ally_lotus",
}

# Ally save abilities
ALLY_SAVE_ABILITIES = {
    "oracle_false_promise": "ally_save",
    "dazzle_shallow_grave": "ally_grave",
    "omniknight_guardian_angel": "ally_immunity",
    "abaddon_aphotic_shield": "ally_shield",
    "shadow_demon_disruption": "ally_banish",
    "outworld_destroyer_astral_imprisonment": "ally_banish",
    "naga_siren_song_of_the_siren": "ally_song",
    "chen_hand_of_god": "ally_heal",
    "io_relocate": "ally_relocate",
}

# Dangerous channeled abilities that can be cancelled
CHANNELED_ABILITIES = {
    "juggernaut_omni_slash",
    "witch_doctor_death_ward",
    "crystal_maiden_freezing_field",
    "enigma_black_hole",
    "bane_fiends_grip",
    "pudge_dismember",
    "shadow_shaman_shackles",
    "pugna_life_drain",
}

# Abilities where target becoming untargetable ends the ability early
TARGET_REQUIRED_ABILITIES = {
    "juggernaut_omni_slash",
    "juggernaut_swiftslash",
    "lifestealer_infest",
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

        # Detect multi-hero abilities (big teamfight abilities like Chrono, Black Hole)
        highlights.multi_hero_abilities = self._detect_multi_hero_abilities(events)

        # Detect generic AoE hits (ANY ability hitting 3+ heroes)
        highlights.generic_aoe_hits = self._detect_generic_aoe_hits(events)

        # Detect kill streaks
        highlights.kill_streaks = self._detect_kill_streaks(deaths)

        # Detect team wipes
        if radiant_heroes and dire_heroes:
            highlights.team_wipes = self._detect_team_wipes(
                deaths, radiant_heroes, dire_heroes
            )

        # Detect fight initiation (legacy single hero)
        initiator, init_ability = self._detect_initiation(events, deaths)
        highlights.fight_initiator = initiator
        highlights.initiation_ability = init_ability

        # Detect BKB + Blink combos (first is initiator, rest are follow-ups)
        highlights.bkb_blink_combos = self._detect_bkb_blink_combos(events)

        # Detect coordinated ultimates
        highlights.coordinated_ults = self._detect_coordinated_ults(events)

        # Detect refresher combos
        highlights.refresher_combos = self._detect_refresher_combos(events)

        # Detect clutch saves
        highlights.clutch_saves = self._detect_clutch_saves(events, deaths)

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

            # Skip self-targeting (e.g., Echo Slam self-damage)
            if target == caster:
                continue

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

    def _detect_generic_aoe_hits(
        self, events: List[CombatLogEvent]
    ) -> List[GenericAoEHit]:
        """
        Detect ANY ability that hit 3+ heroes.

        This is pattern-based - no hardcoded ability list needed.
        Detects things like: 3-man Lina stun, 4-hero Warlock golem hit, etc.
        """
        aoe_hits: List[GenericAoEHit] = []

        # Group ALL ability/damage/modifier events by (ability, time_window)
        # Key: (ability, window_start) -> {targets, caster, first_time}
        ability_windows: Dict[str, Dict] = defaultdict(
            lambda: {"targets": set(), "caster": None, "time": None}
        )

        for event in events:
            ability = self._clean_ability_name(event.ability)
            if not ability:
                continue

            # Skip basic attacks and non-hero targets
            if ability in ("attack", "dota_unknown"):
                continue
            if not event.target_is_hero:
                continue

            target = self._clean_hero_name(event.target)
            caster = self._clean_hero_name(event.attacker)

            # Skip self-targeting
            if target == caster:
                continue

            # Create window key (round to 0.5s windows)
            window_key = f"{ability}_{caster}_{int(event.game_time * 2)}"

            window = ability_windows[window_key]
            window["targets"].add(target)
            if window["caster"] is None:
                window["caster"] = caster
                window["time"] = event.game_time
                window["ability"] = ability

        # Convert windows to GenericAoEHit for abilities hitting 3+ heroes
        for window_data in ability_windows.values():
            window_ability: str = window_data.get("ability", "")
            if not window_ability:
                continue

            targets = list(window_data["targets"])
            hero_count = len(targets)

            # Only report if 3+ heroes were hit
            if hero_count >= GENERIC_AOE_MIN_HEROES:
                # Skip if this is already covered by BIG_TEAMFIGHT_ABILITIES
                # (those are reported in multi_hero_abilities)
                if window_ability in BIG_TEAMFIGHT_ABILITIES:
                    continue

                aoe_hits.append(
                    GenericAoEHit(
                        game_time=window_data["time"],
                        game_time_str=self._format_time(window_data["time"]),
                        ability=window_ability,
                        caster=window_data["caster"],
                        targets=sorted(targets),
                        hero_count=hero_count,
                    )
                )

        # Sort by time
        aoe_hits.sort(key=lambda x: x.game_time)
        return aoe_hits

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

    def _detect_bkb_blink_combos(
        self, events: List[CombatLogEvent]
    ) -> List[BKBBlinkCombo]:
        """
        Detect BKB + Blink combos into big abilities.

        Pattern: BKB + Blink -> Big Ability within BKB_BLINK_WINDOW seconds.
        Accepts either order (BKB->Blink or Blink->BKB).
        First combo is marked as initiator, rest are follow-ups.
        """
        combos: List[BKBBlinkCombo] = []

        # Track BKB and Blink usage per hero
        hero_actions: Dict[str, Dict] = defaultdict(
            lambda: {"bkb_time": None, "blink_time": None}
        )

        sorted_events = sorted(events, key=lambda e: e.game_time)

        for event in sorted_events:
            if event.type != "ITEM":
                # Also check for big abilities after BKB+Blink
                if event.type in ("ABILITY", "DAMAGE") and event.attacker_is_hero:
                    hero = self._clean_hero_name(event.attacker)
                    ability = self._clean_ability_name(event.ability)

                    if ability in BIG_TEAMFIGHT_ABILITIES:
                        actions = hero_actions[hero]
                        bkb_time = actions.get("bkb_time")
                        blink_time = actions.get("blink_time")

                        # Check if BKB+Blink happened recently (either order)
                        if bkb_time and blink_time:
                            if (
                                event.game_time - bkb_time <= BKB_BLINK_WINDOW
                                and event.game_time - blink_time <= BKB_BLINK_WINDOW
                            ):
                                display_name, _ = BIG_TEAMFIGHT_ABILITIES[ability]
                                combos.append(
                                    BKBBlinkCombo(
                                        game_time=event.game_time,
                                        game_time_str=self._format_time(event.game_time),
                                        hero=hero,
                                        ability=ability,
                                        ability_display=display_name,
                                        bkb_time=bkb_time,
                                        blink_time=blink_time,
                                        is_initiator=False,  # Will be set below
                                    )
                                )
                                # Reset to avoid duplicate detection
                                actions["bkb_time"] = None
                                actions["blink_time"] = None
                continue

            ability = self._clean_ability_name(event.ability)
            hero = self._clean_hero_name(event.attacker)

            if ability == "item_black_king_bar":
                hero_actions[hero]["bkb_time"] = event.game_time
            elif ability in BLINK_ITEMS:
                hero_actions[hero]["blink_time"] = event.game_time

        # Mark first combo as initiator
        if combos:
            combos.sort(key=lambda c: c.game_time)
            combos[0].is_initiator = True

        return combos

    def _detect_coordinated_ults(
        self, events: List[CombatLogEvent]
    ) -> List[CoordinatedUltimates]:
        """
        Detect when 2+ heroes use big ultimates together.

        Groups big ability casts within COORDINATED_ULT_WINDOW seconds.
        """
        coordinated: List[CoordinatedUltimates] = []

        # Collect all big ability casts
        ult_casts: List[Tuple[float, str, str]] = []  # (time, hero, ability)

        for event in events:
            if event.type not in ("ABILITY", "DAMAGE"):
                continue
            if not event.attacker_is_hero:
                continue

            ability = self._clean_ability_name(event.ability)
            if ability in BIG_TEAMFIGHT_ABILITIES:
                hero = self._clean_hero_name(event.attacker)
                ult_casts.append((event.game_time, hero, ability))

        # Dedupe by hero+ability (keep first cast only)
        seen = set()
        unique_casts = []
        for time, hero, ability in sorted(ult_casts):
            key = (hero, ability)
            if key not in seen:
                seen.add(key)
                unique_casts.append((time, hero, ability))

        # Find groups within time window
        if len(unique_casts) < 2:
            return coordinated

        # Group casts that are close together
        groups: List[List[Tuple[float, str, str]]] = []
        current_group: List[Tuple[float, str, str]] = [unique_casts[0]]

        for i in range(1, len(unique_casts)):
            time, hero, ability = unique_casts[i]
            if time - current_group[0][0] <= COORDINATED_ULT_WINDOW:
                current_group.append((time, hero, ability))
            else:
                if len(current_group) >= 2:
                    groups.append(current_group)
                current_group = [(time, hero, ability)]

        if len(current_group) >= 2:
            groups.append(current_group)

        # Convert groups to CoordinatedUltimates
        for group in groups:
            heroes = [h for _, h, _ in group]
            abilities = [a for _, _, a in group]
            first_time = group[0][0]
            last_time = group[-1][0]

            coordinated.append(
                CoordinatedUltimates(
                    game_time=first_time,
                    game_time_str=self._format_time(first_time),
                    heroes=heroes,
                    abilities=abilities,
                    window_seconds=last_time - first_time,
                )
            )

        return coordinated

    def _detect_refresher_combos(
        self, events: List[CombatLogEvent]
    ) -> List[RefresherCombo]:
        """
        Detect heroes using Refresher to double-cast ultimates.

        Pattern: Big ability -> Refresher -> Same ability within 5 seconds.
        """
        combos: List[RefresherCombo] = []

        # Track ability casts and refresher usage per hero
        hero_casts: Dict[str, List[Tuple[float, str]]] = defaultdict(list)
        hero_refresher: Dict[str, float] = {}

        sorted_events = sorted(events, key=lambda e: e.game_time)

        for event in sorted_events:
            if not event.attacker_is_hero:
                continue

            hero = self._clean_hero_name(event.attacker)
            ability = self._clean_ability_name(event.ability)

            # Track refresher usage
            if event.type == "ITEM" and ability == "item_refresher":
                hero_refresher[hero] = event.game_time
                continue

            # Track big ability casts
            if event.type in ("ABILITY", "DAMAGE") and ability in BIG_TEAMFIGHT_ABILITIES:
                casts = hero_casts[hero]
                refresher_time = hero_refresher.get(hero)

                # Check if this is a second cast after refresher
                for prev_time, prev_ability in reversed(casts):
                    if prev_ability == ability and refresher_time:
                        if prev_time < refresher_time < event.game_time:
                            if event.game_time - prev_time <= 5.0:
                                display_name, _ = BIG_TEAMFIGHT_ABILITIES[ability]
                                combos.append(
                                    RefresherCombo(
                                        game_time=event.game_time,
                                        game_time_str=self._format_time(event.game_time),
                                        hero=hero,
                                        ability=ability,
                                        ability_display=display_name,
                                        first_cast_time=prev_time,
                                        second_cast_time=event.game_time,
                                    )
                                )
                                # Clear refresher to avoid duplicate detection
                                hero_refresher[hero] = 0
                                break

                casts.append((event.game_time, ability))

        return combos

    def _detect_clutch_saves(
        self,
        events: List[CombatLogEvent],
        deaths: List[HeroDeath],
    ) -> List[ClutchSave]:
        """
        Detect clutch saves - using items/abilities to survive when in danger.

        Only counts as clutch save when:
        - Target was taking significant recent damage (3+ hits in 2s), OR
        - Target was hit by a dangerous ability (Omnislash, etc.)

        NOT clutch saves:
        - Disrupting an ally who isn't under pressure
        - Preemptive saves before any threat
        """
        saves: List[ClutchSave] = []

        # Track who died (so we know who survived)
        dead_heroes = {self._clean_hero_name(d.victim) for d in deaths}

        # Track active dangerous abilities (like Omnislash)
        active_ults: Dict[str, Tuple[float, str]] = {}  # target -> (start_time, ability)

        # Track recent damage taken by heroes: hero -> [(time, damage, ability)]
        recent_damage: Dict[str, List[Tuple[float, int, str]]] = defaultdict(list)

        sorted_events = sorted(events, key=lambda e: e.game_time)

        for event in sorted_events:
            ability = self._clean_ability_name(event.ability)
            attacker = self._clean_hero_name(event.attacker)
            target = self._clean_hero_name(event.target)

            # Track damage taken by heroes (only from other heroes, not towers/creeps)
            if event.type == "DAMAGE" and event.target_is_hero and event.attacker_is_hero:
                damage_value = event.value if event.value else 100  # Assume 100 if unknown
                recent_damage[target].append((event.game_time, damage_value, ability))
                # Keep only recent damage (last 2 seconds)
                recent_damage[target] = [
                    (t, d, a) for t, d, a in recent_damage[target]
                    if event.game_time - t <= 2.0
                ]

            # Track dangerous ability start (like Omnislash targeting someone)
            if ability in TARGET_REQUIRED_ABILITIES and event.target_is_hero:
                if event.type in ("ABILITY", "DAMAGE"):
                    active_ults[target] = (event.game_time, ability)

            # Detect self-save items/abilities
            if event.type == "ITEM" and ability in SELF_SAVE_ITEMS:
                hero = attacker
                save_type = SELF_SAVE_ITEMS[ability]

                # Check if hero was in danger
                was_in_danger = False
                saved_from = None

                # Check for dangerous ability
                if hero in active_ults:
                    ult_start, ult_ability = active_ults[hero]
                    if event.game_time - ult_start <= 3.0:
                        was_in_danger = True
                        saved_from = ult_ability

                # Check for heavy recent damage (3+ hits in 2s)
                if hero in recent_damage and len(recent_damage[hero]) >= 3:
                    was_in_danger = True

                if was_in_danger and hero not in dead_heroes:
                    saves.append(
                        ClutchSave(
                            game_time=event.game_time,
                            game_time_str=self._format_time(event.game_time),
                            saved_hero=hero,
                            save_type=save_type,
                            save_ability=ability,
                            saved_from=saved_from,
                            saver=None,  # Self-save
                        )
                    )
                    if hero in active_ults:
                        del active_ults[hero]

            # Detect ally save items (cast on ally) - ONLY if they were in danger
            if event.type == "ITEM" and ability in ALLY_SAVE_ITEMS:
                if event.target_is_hero and target != attacker:
                    save_type = ALLY_SAVE_ITEMS[ability]

                    # Check if target was in danger
                    was_in_danger = False
                    saved_from = None

                    if target in active_ults:
                        _, saved_from = active_ults[target]
                        was_in_danger = True

                    if target in recent_damage and len(recent_damage[target]) >= 3:
                        was_in_danger = True

                    # Only count if they were in danger AND didn't die
                    if was_in_danger and target not in dead_heroes:
                        saves.append(
                            ClutchSave(
                                game_time=event.game_time,
                                game_time_str=self._format_time(event.game_time),
                                saved_hero=target,
                                save_type=save_type,
                                save_ability=ability,
                                saved_from=saved_from,
                                saver=attacker,
                            )
                        )

            # Detect ally save abilities - ONLY if they were in danger
            if event.type == "ABILITY" and ability in ALLY_SAVE_ABILITIES:
                if event.target_is_hero and target != attacker:
                    save_type = ALLY_SAVE_ABILITIES[ability]

                    was_in_danger = False
                    saved_from = None

                    if target in active_ults:
                        _, saved_from = active_ults[target]
                        was_in_danger = True

                    if target in recent_damage and len(recent_damage[target]) >= 3:
                        was_in_danger = True

                    if was_in_danger and target not in dead_heroes:
                        saves.append(
                            ClutchSave(
                                game_time=event.game_time,
                                game_time_str=self._format_time(event.game_time),
                                saved_hero=target,
                                save_type=save_type,
                                save_ability=ability,
                                saved_from=saved_from,
                                saver=attacker,
                            )
                        )

        return saves
