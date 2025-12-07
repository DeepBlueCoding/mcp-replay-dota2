"""
Tests for FightAnalyzer - fight highlight detection.

Tests multi-hero ability detection, kill streaks, and team wipes.
"""


from src.services.analyzers.fight_analyzer import (
    BIG_TEAMFIGHT_ABILITIES,
    KILL_STREAK_WINDOW,
    FightAnalyzer,
)
from src.services.models.combat_data import (
    CombatLogEvent,
    FightHighlights,
    HeroDeath,
)


class TestFightAnalyzerInit:
    """Basic initialization tests."""

    def test_analyzer_instantiates(self):
        analyzer = FightAnalyzer()
        assert analyzer is not None

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


class TestMultiHeroAbilityDetection:
    """Tests for detecting abilities that hit multiple heroes."""

    def test_detect_chronosphere_hitting_3_heroes(self):
        """Chronosphere hitting 3 heroes should be detected."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="MODIFIER_ADD",
                game_time=600.0,
                game_time_str="10:00",
                tick=18000,
                attacker="faceless_void",
                attacker_is_hero=True,
                target="antimage",
                target_is_hero=True,
                ability="modifier_faceless_void_chronosphere_freeze",
            ),
            CombatLogEvent(
                type="MODIFIER_ADD",
                game_time=600.01,
                game_time_str="10:00",
                tick=18001,
                attacker="faceless_void",
                attacker_is_hero=True,
                target="crystal_maiden",
                target_is_hero=True,
                ability="modifier_faceless_void_chronosphere_freeze",
            ),
            CombatLogEvent(
                type="MODIFIER_ADD",
                game_time=600.02,
                game_time_str="10:00",
                tick=18002,
                attacker="faceless_void",
                attacker_is_hero=True,
                target="lion",
                target_is_hero=True,
                ability="modifier_faceless_void_chronosphere_freeze",
            ),
        ]

        highlights = analyzer.analyze_fight(events, [])

        assert len(highlights.multi_hero_abilities) == 1
        mha = highlights.multi_hero_abilities[0]
        assert mha.ability == "faceless_void_chronosphere"
        assert mha.ability_display == "Chronosphere"
        assert mha.caster == "faceless_void"
        assert mha.hero_count == 3
        assert set(mha.targets) == {"antimage", "crystal_maiden", "lion"}

    def test_ability_hitting_only_1_hero_not_detected(self):
        """Single-target ability should not be in multi_hero_abilities."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=600.0,
                game_time_str="10:00",
                tick=18000,
                attacker="faceless_void",
                attacker_is_hero=True,
                target="antimage",
                target_is_hero=True,
                ability="faceless_void_chronosphere",
            ),
        ]

        highlights = analyzer.analyze_fight(events, [])

        # Should not be detected since only 1 hero hit (min is 2)
        assert len(highlights.multi_hero_abilities) == 0

    def test_ice_path_hitting_2_heroes(self):
        """Ice Path hitting 2 heroes should be detected."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=500.0,
                game_time_str="8:20",
                tick=15000,
                attacker="jakiro",
                attacker_is_hero=True,
                target="juggernaut",
                target_is_hero=True,
                ability="jakiro_ice_path",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=500.1,
                game_time_str="8:20",
                tick=15003,
                attacker="jakiro",
                attacker_is_hero=True,
                target="shadow_fiend",
                target_is_hero=True,
                ability="jakiro_ice_path",
            ),
        ]

        highlights = analyzer.analyze_fight(events, [])

        assert len(highlights.multi_hero_abilities) == 1
        mha = highlights.multi_hero_abilities[0]
        assert mha.ability == "jakiro_ice_path"
        assert mha.ability_display == "Ice Path"
        assert mha.hero_count == 2


class TestKillStreakDetection:
    """Tests for kill streak detection."""

    def test_detect_double_kill(self):
        """Two kills by same hero within 18s = double kill."""
        analyzer = FightAnalyzer()

        deaths = [
            HeroDeath(
                game_time=600.0,
                game_time_str="10:00",
                tick=18000,
                killer="medusa",
                victim="antimage",
                killer_is_hero=True,
            ),
            HeroDeath(
                game_time=605.0,
                game_time_str="10:05",
                tick=18150,
                killer="medusa",
                victim="lion",
                killer_is_hero=True,
            ),
        ]

        highlights = analyzer.analyze_fight([], deaths)

        assert len(highlights.kill_streaks) == 1
        streak = highlights.kill_streaks[0]
        assert streak.hero == "medusa"
        assert streak.streak_type == "double_kill"
        assert streak.kills == 2
        assert set(streak.victims) == {"antimage", "lion"}

    def test_detect_rampage(self):
        """Five kills by same hero within 18s = rampage."""
        analyzer = FightAnalyzer()

        deaths = [
            HeroDeath(
                game_time=600.0 + i * 3,
                game_time_str=f"10:{i*3:02d}",
                tick=18000 + i * 90,
                killer="medusa",
                victim=f"hero_{i}",
                killer_is_hero=True,
            )
            for i in range(5)
        ]

        highlights = analyzer.analyze_fight([], deaths)

        assert len(highlights.kill_streaks) == 1
        streak = highlights.kill_streaks[0]
        assert streak.hero == "medusa"
        assert streak.streak_type == "rampage"
        assert streak.kills == 5

    def test_no_streak_if_kills_too_far_apart(self):
        """Kills more than 18s apart should not form a streak."""
        analyzer = FightAnalyzer()

        deaths = [
            HeroDeath(
                game_time=600.0,
                game_time_str="10:00",
                tick=18000,
                killer="medusa",
                victim="antimage",
                killer_is_hero=True,
            ),
            HeroDeath(
                game_time=620.0,  # 20 seconds later
                game_time_str="10:20",
                tick=18600,
                killer="medusa",
                victim="lion",
                killer_is_hero=True,
            ),
        ]

        highlights = analyzer.analyze_fight([], deaths)

        # No streak since kills are >18s apart
        assert len(highlights.kill_streaks) == 0


class TestTeamWipeDetection:
    """Tests for team wipe (ace) detection."""

    def test_detect_radiant_team_wipe(self):
        """All 5 radiant heroes dying = team wipe."""
        analyzer = FightAnalyzer()

        radiant_heroes = {"antimage", "crystal_maiden", "lion", "earthshaker", "tidehunter"}
        dire_heroes = {"medusa", "disruptor", "naga_siren", "invoker", "mars"}

        deaths = [
            HeroDeath(
                game_time=600.0 + i * 2,
                game_time_str=f"10:{i*2:02d}",
                tick=18000 + i * 60,
                killer="medusa",
                victim=hero,
                killer_is_hero=True,
            )
            for i, hero in enumerate(radiant_heroes)
        ]

        highlights = analyzer.analyze_fight([], deaths, radiant_heroes, dire_heroes)

        assert len(highlights.team_wipes) == 1
        wipe = highlights.team_wipes[0]
        assert wipe.team_wiped == "radiant"
        assert wipe.killer_team == "dire"
        assert wipe.duration == 8.0  # 4 heroes * 2s each

    def test_no_team_wipe_if_only_4_die(self):
        """Only 4 of 5 heroes dying is not a team wipe."""
        analyzer = FightAnalyzer()

        radiant_heroes = {"antimage", "crystal_maiden", "lion", "earthshaker", "tidehunter"}
        dire_heroes = {"medusa", "disruptor", "naga_siren", "invoker", "mars"}

        # Only 4 radiant heroes die
        deaths = [
            HeroDeath(
                game_time=600.0 + i * 2,
                game_time_str=f"10:{i*2:02d}",
                tick=18000 + i * 60,
                killer="medusa",
                victim=hero,
                killer_is_hero=True,
            )
            for i, hero in enumerate(list(radiant_heroes)[:4])
        ]

        highlights = analyzer.analyze_fight([], deaths, radiant_heroes, dire_heroes)

        assert len(highlights.team_wipes) == 0


class TestInitiationDetection:
    """Tests for fight initiation detection."""

    def test_detect_black_hole_initiation(self):
        """Black Hole as first big ability should be detected as initiation."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=600.0,
                game_time_str="10:00",
                tick=18000,
                attacker="enigma",
                attacker_is_hero=True,
                target="antimage",
                target_is_hero=True,
                ability="enigma_black_hole",
            ),
            CombatLogEvent(
                type="DEATH",
                game_time=603.0,
                game_time_str="10:03",
                tick=18090,
                attacker="medusa",
                attacker_is_hero=True,
                target="antimage",
                target_is_hero=True,
            ),
        ]

        highlights = analyzer.analyze_fight(events, [])

        assert highlights.fight_initiator == "enigma"
        assert highlights.initiation_ability == "Black Hole"


class TestHighlightsModel:
    """Tests for FightHighlights dataclass."""

    def test_empty_highlights(self):
        """Empty highlights should have empty lists."""
        highlights = FightHighlights()
        assert highlights.multi_hero_abilities == []
        assert highlights.kill_streaks == []
        assert highlights.team_wipes == []
        assert highlights.fight_initiator is None
        assert highlights.initiation_ability is None
