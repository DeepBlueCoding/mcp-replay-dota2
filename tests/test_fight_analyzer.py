"""
Tests for FightAnalyzer - fight highlight detection.

Tests multi-hero ability detection, kill streaks, and team wipes.
"""


from src.services.analyzers.fight_analyzer import (
    BIG_TEAMFIGHT_ABILITIES,
    BLINK_ITEMS,
    KILL_STREAK_WINDOW,
    SELF_SAVE_ITEMS,
    TARGET_REQUIRED_ABILITIES,
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

    def test_new_highlight_fields_exist(self):
        """New highlight fields should exist and default to empty."""
        highlights = FightHighlights()
        assert highlights.bkb_blink_combos == []
        assert highlights.coordinated_ults == []
        assert highlights.refresher_combos == []
        assert highlights.clutch_saves == []


class TestNewConstants:
    """Tests for new fight analyzer constants."""

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


class TestBKBBlinkCombo:
    """Tests for BKB + Blink combo detection."""

    def test_detects_bkb_blink_echo_slam(self):
        """Should detect BKB -> Blink -> Echo Slam pattern."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ITEM",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_black_king_bar",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2801.2,
                game_time_str="46:41",
                tick=101,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_blink",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.5,
                game_time_str="46:41",
                tick=102,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
        ]

        combos = analyzer._detect_bkb_blink_combos(events)

        assert len(combos) == 1
        assert combos[0].hero == "earthshaker"
        assert combos[0].ability == "earthshaker_echo_slam"
        assert combos[0].ability_display == "Echo Slam"
        assert combos[0].bkb_time == 2801.0
        assert combos[0].blink_time == 2801.2
        assert combos[0].is_initiator is True  # First combo is initiator

    def test_detects_blink_before_bkb(self):
        """Should detect Blink -> BKB -> Ability pattern (either order is valid)."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ITEM",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_nevermore",
                target_is_hero=True,
                ability="item_blink",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2801.2,
                game_time_str="46:41",
                tick=101,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_nevermore",
                target_is_hero=True,
                ability="item_black_king_bar",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.5,
                game_time_str="46:41",
                tick=102,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="nevermore_requiem",
            ),
        ]

        combos = analyzer._detect_bkb_blink_combos(events)
        assert len(combos) == 1
        assert combos[0].hero == "nevermore"
        assert combos[0].ability_display == "Requiem of Souls"
        assert combos[0].is_initiator is True

    def test_first_combo_is_initiator_rest_followup(self):
        """First BKB+Blink combo is initiator, subsequent ones are follow-ups."""
        analyzer = FightAnalyzer()

        events = [
            # ES initiates first
            CombatLogEvent(
                type="ITEM",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_black_king_bar",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2801.1,
                game_time_str="46:41",
                tick=101,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_blink",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.3,
                game_time_str="46:41",
                tick=102,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
            # SF follows up
            CombatLogEvent(
                type="ITEM",
                game_time=2801.5,
                game_time_str="46:41",
                tick=103,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_nevermore",
                target_is_hero=True,
                ability="item_blink",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2801.6,
                game_time_str="46:41",
                tick=104,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_nevermore",
                target_is_hero=True,
                ability="item_black_king_bar",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.8,
                game_time_str="46:41",
                tick=105,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="nevermore_requiem",
            ),
        ]

        combos = analyzer._detect_bkb_blink_combos(events)

        assert len(combos) == 2
        # ES is first = initiator
        assert combos[0].hero == "earthshaker"
        assert combos[0].is_initiator is True
        # SF is second = follow-up
        assert combos[1].hero == "nevermore"
        assert combos[1].is_initiator is False

    def test_ignores_outside_time_window(self):
        """Should not detect if ability is too far after BKB+Blink."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ITEM",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_black_king_bar",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2801.2,
                game_time_str="46:41",
                tick=101,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_blink",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2805.0,
                game_time_str="46:45",
                tick=202,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
        ]

        combos = analyzer._detect_bkb_blink_combos(events)
        assert len(combos) == 0


class TestCoordinatedUltimates:
    """Tests for coordinated ultimates detection."""

    def test_detects_two_heroes_ulting_together(self):
        """Should detect when 2+ heroes use big abilities together."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2802.5,
                game_time_str="46:42",
                tick=150,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="nevermore_requiem",
            ),
        ]

        coordinated = analyzer._detect_coordinated_ults(events)

        assert len(coordinated) == 1
        assert "earthshaker" in coordinated[0].heroes
        assert "nevermore" in coordinated[0].heroes
        assert coordinated[0].window_seconds == 1.5

    def test_detects_three_heroes_ulting_together(self):
        """Should detect coordinated 3-hero ult combo."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.5,
                game_time_str="46:41",
                tick=120,
                attacker="npc_dota_hero_medusa",
                attacker_is_hero=True,
                target="npc_dota_hero_juggernaut",
                target_is_hero=True,
                ability="medusa_stone_gaze",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2802.7,
                game_time_str="46:42",
                tick=160,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="nevermore_requiem",
            ),
        ]

        coordinated = analyzer._detect_coordinated_ults(events)

        assert len(coordinated) == 1
        assert len(coordinated[0].heroes) == 3
        assert "earthshaker" in coordinated[0].heroes
        assert "medusa" in coordinated[0].heroes
        assert "nevermore" in coordinated[0].heroes

    def test_ignores_solo_ult(self):
        """Should not report single hero ulting alone."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
        ]

        coordinated = analyzer._detect_coordinated_ults(events)
        assert len(coordinated) == 0


class TestRefresherCombo:
    """Tests for Refresher double ultimate detection."""

    def test_detects_double_echo_slam(self):
        """Should detect ES using Refresher for double Echo Slam."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2802.0,
                game_time_str="46:42",
                tick=120,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="item_refresher",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2803.0,
                game_time_str="46:43",
                tick=140,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_magnus",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
        ]

        combos = analyzer._detect_refresher_combos(events)

        assert len(combos) == 1
        assert combos[0].hero == "earthshaker"
        assert combos[0].ability == "earthshaker_echo_slam"
        assert combos[0].ability_display == "Echo Slam"
        assert combos[0].first_cast_time == 2801.0
        assert combos[0].second_cast_time == 2803.0

    def test_ignores_same_ability_without_refresher(self):
        """Should not detect double cast without Refresher in between."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
            CombatLogEvent(
                type="ABILITY",
                game_time=2803.0,
                game_time_str="46:43",
                tick=140,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_magnus",
                target_is_hero=True,
                ability="earthshaker_echo_slam",
            ),
        ]

        combos = analyzer._detect_refresher_combos(events)
        assert len(combos) == 0


class TestClutchSaves:
    """Tests for clutch save detection."""

    def test_detects_outworld_staff_save_from_omnislash(self):
        """Should detect Medusa using Outworld Staff to escape Omnislash."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2810.0,
                game_time_str="46:50",
                tick=500,
                attacker="npc_dota_hero_juggernaut",
                attacker_is_hero=True,
                target="npc_dota_hero_medusa",
                target_is_hero=True,
                ability="juggernaut_omni_slash",
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2810.5,
                game_time_str="46:50",
                tick=520,
                attacker="npc_dota_hero_juggernaut",
                attacker_is_hero=True,
                target="npc_dota_hero_medusa",
                target_is_hero=True,
                ability="juggernaut_omni_slash",
                value=150,
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2811.0,
                game_time_str="46:51",
                tick=540,
                attacker="npc_dota_hero_medusa",
                attacker_is_hero=True,
                target="npc_dota_hero_medusa",
                target_is_hero=True,
                ability="item_outworld_staff",
            ),
        ]

        deaths = []
        saves = analyzer._detect_clutch_saves(events, deaths)

        assert len(saves) == 1
        assert saves[0].saved_hero == "medusa"
        assert saves[0].save_type == "self_banish"
        assert saves[0].save_ability == "item_outworld_staff"
        assert saves[0].saved_from == "juggernaut_omni_slash"
        assert saves[0].saver is None

    def test_no_save_if_target_dies(self):
        """Should not count as save if target dies anyway."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ABILITY",
                game_time=2810.0,
                game_time_str="46:50",
                tick=500,
                attacker="npc_dota_hero_juggernaut",
                attacker_is_hero=True,
                target="npc_dota_hero_medusa",
                target_is_hero=True,
                ability="juggernaut_omni_slash",
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2811.0,
                game_time_str="46:51",
                tick=540,
                attacker="npc_dota_hero_medusa",
                attacker_is_hero=True,
                target="npc_dota_hero_medusa",
                target_is_hero=True,
                ability="item_outworld_staff",
            ),
        ]

        deaths = [
            HeroDeath(
                game_time=2812.0,
                game_time_str="46:52",
                tick=560,
                killer="npc_dota_hero_juggernaut",
                victim="npc_dota_hero_medusa",
                killer_is_hero=True,
            )
        ]

        saves = analyzer._detect_clutch_saves(events, deaths)
        assert len(saves) == 0

    def test_detects_ally_glimmer_save(self):
        """Should detect ally using Glimmer Cape to save teammate who was under attack."""
        analyzer = FightAnalyzer()

        # Pangolier needs to be under attack (3+ hero damage hits) for save to count
        events = [
            CombatLogEvent(
                type="DAMAGE",
                game_time=2808.0,
                game_time_str="46:48",
                tick=498,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_pangolier",
                target_is_hero=True,
                ability="nevermore_shadowraze1",
                value=200,
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2809.0,
                game_time_str="46:49",
                tick=499,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_pangolier",
                target_is_hero=True,
                ability="earthshaker_fissure",
                value=150,
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2809.5,
                game_time_str="46:49",
                tick=499,
                attacker="npc_dota_hero_nevermore",
                attacker_is_hero=True,
                target="npc_dota_hero_pangolier",
                target_is_hero=True,
                ability="attack",
                value=100,
            ),
            CombatLogEvent(
                type="ITEM",
                game_time=2810.0,
                game_time_str="46:50",
                tick=500,
                attacker="npc_dota_hero_disruptor",
                attacker_is_hero=True,
                target="npc_dota_hero_pangolier",
                target_is_hero=True,
                ability="item_glimmer_cape",
            ),
        ]

        deaths = []
        saves = analyzer._detect_clutch_saves(events, deaths)

        assert len(saves) == 1
        assert saves[0].saved_hero == "pangolier"
        assert saves[0].save_type == "ally_glimmer"
        assert saves[0].save_ability == "item_glimmer_cape"
        assert saves[0].saver == "disruptor"

    def test_ignores_self_glimmer(self):
        """Self-Glimmer should not be tracked as ally save."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="ITEM",
                game_time=2810.0,
                game_time_str="46:50",
                tick=500,
                attacker="npc_dota_hero_disruptor",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="item_glimmer_cape",
            ),
        ]

        deaths = []
        saves = analyzer._detect_clutch_saves(events, deaths)

        # Should not be tracked since self-Glimmer
        assert len(saves) == 0


class TestGenericAoEHits:
    """Tests for generic AoE detection (any ability hitting 3+ heroes)."""

    def test_filters_self_targeting(self):
        """Should not count self-targeting in hero count."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="DAMAGE",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_earthshaker",
                target_is_hero=True,
                ability="some_custom_ability",
                value=300,
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="some_custom_ability",
                value=300,
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_earthshaker",
                attacker_is_hero=True,
                target="npc_dota_hero_magnus",
                target_is_hero=True,
                ability="some_custom_ability",
                value=300,
            ),
        ]

        aoe_hits = analyzer._detect_generic_aoe_hits(events)
        assert len(aoe_hits) == 0

    def test_detects_unknown_ability_hitting_3_heroes(self):
        """Should detect any ability hitting 3+ different heroes."""
        analyzer = FightAnalyzer()

        events = [
            CombatLogEvent(
                type="DAMAGE",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_lina",
                attacker_is_hero=True,
                target="npc_dota_hero_disruptor",
                target_is_hero=True,
                ability="lina_light_strike_array",
                value=200,
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_lina",
                attacker_is_hero=True,
                target="npc_dota_hero_magnus",
                target_is_hero=True,
                ability="lina_light_strike_array",
                value=200,
            ),
            CombatLogEvent(
                type="DAMAGE",
                game_time=2801.0,
                game_time_str="46:41",
                tick=100,
                attacker="npc_dota_hero_lina",
                attacker_is_hero=True,
                target="npc_dota_hero_juggernaut",
                target_is_hero=True,
                ability="lina_light_strike_array",
                value=200,
            ),
        ]

        aoe_hits = analyzer._detect_generic_aoe_hits(events)
        assert len(aoe_hits) == 1
        assert aoe_hits[0].hero_count == 3
        assert aoe_hits[0].caster == "lina"
        assert aoe_hits[0].ability == "lina_light_strike_array"
