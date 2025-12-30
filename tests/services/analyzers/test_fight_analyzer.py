"""
Tests for FightAnalyzer - fight highlight detection.

Tests verify ACTUAL VALUES from real match data, not just "can I call this API".
"""

import pytest

from src.services.analyzers.fight_analyzer import (
    BIG_TEAMFIGHT_ABILITIES,
    BLINK_ITEMS,
    KILL_STREAK_WINDOW,
    SELF_SAVE_ITEMS,
    TARGET_REQUIRED_ABILITIES,
)
from src.services.combat.fight_service import FightService


class TestFightAnalyzerConstants:
    """Tests for FightAnalyzer constants."""

    def test_big_abilities_defined(self):
        """Key teamfight abilities are defined."""
        assert "faceless_void_chronosphere" in BIG_TEAMFIGHT_ABILITIES
        assert "enigma_black_hole" in BIG_TEAMFIGHT_ABILITIES
        assert "magnataur_reverse_polarity" in BIG_TEAMFIGHT_ABILITIES
        assert "tidehunter_ravage" in BIG_TEAMFIGHT_ABILITIES
        assert "jakiro_ice_path" in BIG_TEAMFIGHT_ABILITIES

    def test_kill_streak_window_is_18_seconds(self):
        """Dota 2 uses 18 second window for kill streaks."""
        assert KILL_STREAK_WINDOW == 18.0

    def test_blink_items_includes_all_variants(self):
        """All blink variants should be tracked."""
        assert "item_blink" in BLINK_ITEMS
        assert "item_swift_blink" in BLINK_ITEMS
        assert "item_arcane_blink" in BLINK_ITEMS
        assert "item_overwhelming_blink" in BLINK_ITEMS

    def test_self_save_items_includes_outworld_staff(self):
        """Outworld Staff should be tracked as self-banish."""
        assert "item_outworld_staff" in SELF_SAVE_ITEMS
        assert SELF_SAVE_ITEMS["item_outworld_staff"] == "self_banish"

    def test_target_required_abilities_includes_omnislash(self):
        """Omnislash variants should be tracked."""
        assert "juggernaut_omni_slash" in TARGET_REQUIRED_ABILITIES
        assert "juggernaut_swiftslash" in TARGET_REQUIRED_ABILITIES

    def test_requiem_alias_tracked(self):
        """Both requiem ability names should be tracked."""
        assert "shadow_fiend_requiem_of_souls" in BIG_TEAMFIGHT_ABILITIES
        assert "nevermore_requiem" in BIG_TEAMFIGHT_ABILITIES


class TestMatch8461956309Fights:
    """Tests for fight data in match 8461956309 - verifies ACTUAL VALUES."""

    def test_total_fights_is_24(self, all_fights):
        """Match 8461956309 has exactly 24 fights detected."""
        assert all_fights.total_fights == 24

    def test_total_deaths_is_31(self, all_fights):
        """Match 8461956309 has exactly 31 deaths across all fights."""
        assert all_fights.total_deaths == 31

    def test_teamfights_count_is_0(self, all_fights):
        """Match has 0 teamfights (no fights with 3+ deaths)."""
        teamfights = [f for f in all_fights.fights if f.is_teamfight]
        assert len(teamfights) == 0

    def test_first_fight_is_first_blood_at_4_48(self, all_fights):
        """First fight is first blood - Earthshaker killed by Disruptor at 4:48."""
        first_fight = all_fights.fights[0]
        assert first_fight.start_time_str == "4:48"
        assert first_fight.total_deaths == 1
        assert first_fight.deaths[0].victim == "earthshaker"
        assert first_fight.deaths[0].killer == "disruptor"

    def test_fight_at_48_08_has_2_deaths(self, all_fights):
        """Fight at 48:08 has 2 deaths (ES double kill)."""
        fight_4808 = next(
            (f for f in all_fights.fights if f.start_time_str == "48:08"),
            None
        )
        assert fight_4808 is not None, "Fight at 48:08 not found"
        assert fight_4808.total_deaths == 2
        # Earthshaker killed Disruptor and Magnus
        victims = {d.victim for d in fight_4808.deaths}
        assert victims == {"disruptor", "magnataur"}


class TestMatch8461956309Highlights:
    """Tests for fight highlights in match 8461956309 - verifies ACTUAL VALUES."""

    @pytest.fixture(scope="class")
    def all_highlights(self, parsed_replay_data, all_fights):
        """Collect all highlights from all fights using death-based detection."""
        fs = FightService()
        highlights = {
            "multi_hero_abilities": [],
            "kill_streaks": [],
            "bkb_blink_combos": [],
            "coordinated_ults": [],
            "clutch_saves": [],
        }
        for fight in all_fights.fights:
            # Use death-based detection to match fight boundaries from all_fights
            context = fs.get_fight_combat_log(
                parsed_replay_data, fight.start_time, use_combat_detection=False
            )
            if context and "highlights" in context:
                hl = context["highlights"]
                highlights["multi_hero_abilities"].extend(hl.multi_hero_abilities)
                highlights["kill_streaks"].extend(hl.kill_streaks)
                highlights["bkb_blink_combos"].extend(hl.bkb_blink_combos)
                highlights["coordinated_ults"].extend(hl.coordinated_ults)
                highlights["clutch_saves"].extend(hl.clutch_saves)
        return highlights

    def test_total_multi_hero_abilities_is_5(self, all_highlights):
        """Match has exactly 5 multi-hero ability hits."""
        assert len(all_highlights["multi_hero_abilities"]) == 5

    def test_earthshaker_fissure_hits_2_heroes_4_times(self, all_highlights):
        """Earthshaker Fissure hit 2 heroes in 4 separate fights."""
        fissures = [
            mha for mha in all_highlights["multi_hero_abilities"]
            if "fissure" in mha.ability.lower() and mha.caster == "earthshaker"
        ]
        assert len(fissures) == 4
        assert all(f.hero_count == 2 for f in fissures)

    def test_disruptor_static_storm_hits_2_heroes(self, all_highlights):
        """Disruptor Static Storm hit 2 heroes once."""
        storms = [
            mha for mha in all_highlights["multi_hero_abilities"]
            if "static_storm" in mha.ability.lower() and mha.caster == "disruptor"
        ]
        assert len(storms) == 1
        assert storms[0].hero_count == 2

    def test_total_kill_streaks_is_2(self, all_highlights):
        """Match has exactly 2 kill streaks."""
        assert len(all_highlights["kill_streaks"]) == 2

    def test_earthshaker_has_double_kill(self, all_highlights):
        """Earthshaker got a double kill."""
        es_streaks = [
            ks for ks in all_highlights["kill_streaks"]
            if ks.hero == "earthshaker"
        ]
        assert len(es_streaks) == 1
        assert es_streaks[0].streak_type == "double_kill"

    def test_medusa_has_double_kill(self, all_highlights):
        """Medusa got a double kill."""
        medusa_streaks = [
            ks for ks in all_highlights["kill_streaks"]
            if ks.hero == "medusa"
        ]
        assert len(medusa_streaks) == 1
        assert medusa_streaks[0].streak_type == "double_kill"

    def test_no_bkb_blink_combos(self, all_highlights):
        """Match has no detected BKB+Blink combos."""
        assert len(all_highlights["bkb_blink_combos"]) == 0

    def test_no_coordinated_ults(self, all_highlights):
        """Match has no detected coordinated ultimates."""
        assert len(all_highlights["coordinated_ults"]) == 0

    def test_no_clutch_saves(self, all_highlights):
        """Match has no detected clutch saves."""
        assert len(all_highlights["clutch_saves"]) == 0


class TestTeamHeroesExtraction:
    """Tests for team hero extraction from entity snapshots."""

    def test_finds_all_10_heroes(self, team_heroes):
        """Should find all 10 heroes (5 per team)."""
        radiant, dire = team_heroes
        assert len(radiant) == 5
        assert len(dire) == 5

    def test_radiant_heroes_correct(self, team_heroes):
        """Radiant team should have correct heroes for match 8461956309."""
        radiant, _ = team_heroes
        expected_radiant = {"earthshaker", "juggernaut", "nevermore", "shadow_demon", "pugna"}
        assert radiant == expected_radiant

    def test_dire_heroes_correct(self, team_heroes):
        """Dire team should have correct heroes for match 8461956309."""
        _, dire = team_heroes
        expected_dire = {"disruptor", "medusa", "naga_siren", "pangolier", "magnataur"}
        assert dire == expected_dire

    def test_no_hero_overlap(self, team_heroes):
        """No hero should be on both teams."""
        radiant, dire = team_heroes
        overlap = radiant & dire
        assert len(overlap) == 0, f"Heroes on both teams: {overlap}"


class TestFightLocations:
    """Tests for fight location classification with tower-based detection."""

    def test_first_blood_location_is_dire_t1_top(self, parsed_replay_data):
        """First blood (Earthshaker at 4:48) happened near Dire T1 top tower."""
        from src.services.combat.fight_service import FightService
        fs = FightService()
        summary = fs.get_fight_summary(parsed_replay_data)
        first_fight = summary["fights"][0]
        assert first_fight["location"] == "dire_t1_top"

    def test_mid_fight_location_is_radiant_t1_mid(self, parsed_replay_data):
        """Fight at 6:06 (Pangolier death) was near Radiant T1 mid tower."""
        from src.services.combat.fight_service import FightService
        fs = FightService()
        summary = fs.get_fight_summary(parsed_replay_data)
        fight_606 = next(
            (f for f in summary["fights"] if f["start_time_str"] == "6:06"),
            None
        )
        assert fight_606 is not None
        assert fight_606["location"] == "radiant_t1_mid"

    def test_bot_fight_location_is_dire_t1_bot(self, parsed_replay_data):
        """Fight at 9:11 (Magnus death) was near Dire T1 bot tower."""
        from src.services.combat.fight_service import FightService
        fs = FightService()
        summary = fs.get_fight_summary(parsed_replay_data)
        fight_911 = next(
            (f for f in summary["fights"] if f["start_time_str"] == "9:11"),
            None
        )
        assert fight_911 is not None
        assert fight_911["location"] == "dire_t1_bot"

    def test_location_filter_t1_finds_tower_fights(self, parsed_replay_data):
        """Location filter 't1' finds all T1 tower fights."""
        from src.services.combat.fight_service import FightService
        fs = FightService()
        summary = fs.get_fight_summary(parsed_replay_data)
        t1_fights = [f for f in summary["fights"] if f.get("location") and "t1" in f["location"]]
        assert len(t1_fights) == 6


class TestMatch8594217096Fights:
    """Tests for fight data in match 8594217096 (OG match) - verifies ACTUAL VALUES."""

    def test_total_fights_is_31(self, all_fights_2):
        """Match 8594217096 has exactly 31 fights detected."""
        assert all_fights_2.total_fights == 31

    def test_total_deaths_is_54(self, all_fights_2):
        """Match 8594217096 has exactly 54 deaths across all fights."""
        assert all_fights_2.total_deaths == 54

    def test_first_fight_is_pregame_snapfire(self, all_fights_2):
        """First fight is pre-game Snapfire death at -1:35 by Void Spirit."""
        first_fight = all_fights_2.fights[0]
        assert first_fight.start_time_str == "-1:35"
        assert first_fight.deaths[0].victim == "snapfire"
        assert first_fight.deaths[0].killer == "void_spirit"

    def test_first_blood_at_1_24(self, all_fights_2):
        """First blood (after game start) was Batrider at 1:24."""
        # Find first fight after game start (time > 0)
        first_game_fight = next(
            (f for f in all_fights_2.fights if f.start_time > 0),
            None
        )
        assert first_game_fight is not None
        assert first_game_fight.start_time_str == "1:24"
        assert first_game_fight.deaths[0].victim == "batrider"
        assert first_game_fight.deaths[0].killer == "pugna"

    def test_teamfights_count_is_7(self, all_fights_2):
        """Match has exactly 7 teamfights (fights with 3+ deaths)."""
        teamfights = [f for f in all_fights_2.fights if f.is_teamfight]
        assert len(teamfights) == 7
