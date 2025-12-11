"""Tests for position (1-5) assignment logic."""

from src.models.match_info import DraftAction, HeroMatchupInfo
from src.models.tool_responses import HeroStats, MatchPlayerInfo
from src.utils.match_fetcher import assign_positions, get_lane_name


class TestAssignPositions:
    """Tests for assign_positions function."""

    def test_standard_lanes_all_positions_assigned(self):
        """All 5 positions should be assigned for a standard team layout."""
        players = [
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 600},  # pos 1
            {"player_slot": 1, "lane_role": 2, "gold_per_min": 550},  # pos 2
            {"player_slot": 2, "lane_role": 3, "gold_per_min": 450},  # pos 3
            {"player_slot": 3, "lane_role": 1, "gold_per_min": 250},  # pos 5 (safelane support)
            {"player_slot": 4, "lane_role": 3, "gold_per_min": 300},  # pos 4 (offlane support)
        ]

        assign_positions(players)

        positions = sorted([p["position"] for p in players])
        assert positions == [1, 2, 3, 4, 5]

    def test_safelane_core_gets_position_1(self):
        """Highest GPM safelane player should be pos 1."""
        players = [
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 650},
            {"player_slot": 1, "lane_role": 1, "gold_per_min": 250},
            {"player_slot": 2, "lane_role": 2, "gold_per_min": 500},
            {"player_slot": 3, "lane_role": 3, "gold_per_min": 400},
            {"player_slot": 4, "lane_role": 3, "gold_per_min": 280},
        ]

        assign_positions(players)

        carry = next(p for p in players if p["gold_per_min"] == 650)
        assert carry["position"] == 1
        assert carry["role"] == "core"

    def test_mid_gets_position_2(self):
        """Mid lane player should be pos 2."""
        players = [
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 600},
            {"player_slot": 1, "lane_role": 2, "gold_per_min": 580},  # mid
            {"player_slot": 2, "lane_role": 3, "gold_per_min": 450},
            {"player_slot": 3, "lane_role": 1, "gold_per_min": 250},
            {"player_slot": 4, "lane_role": 3, "gold_per_min": 300},
        ]

        assign_positions(players)

        mid = next(p for p in players if p["lane_role"] == 2)
        assert mid["position"] == 2
        assert mid["role"] == "core"

    def test_offlane_core_gets_position_3(self):
        """Highest GPM offlane player should be pos 3."""
        players = [
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 600},
            {"player_slot": 1, "lane_role": 2, "gold_per_min": 550},
            {"player_slot": 2, "lane_role": 3, "gold_per_min": 480},  # offlane core
            {"player_slot": 3, "lane_role": 1, "gold_per_min": 250},
            {"player_slot": 4, "lane_role": 3, "gold_per_min": 290},  # offlane support
        ]

        assign_positions(players)

        offlane_core = next(p for p in players if p["lane_role"] == 3 and p["gold_per_min"] == 480)
        assert offlane_core["position"] == 3
        assert offlane_core["role"] == "core"

    def test_supports_get_positions_4_and_5(self):
        """Supports should get pos 4 (higher GPM) and pos 5 (lower GPM)."""
        players = [
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 600},
            {"player_slot": 1, "lane_role": 2, "gold_per_min": 550},
            {"player_slot": 2, "lane_role": 3, "gold_per_min": 450},
            {"player_slot": 3, "lane_role": 1, "gold_per_min": 280},  # pos 4 (higher GPM support)
            {"player_slot": 4, "lane_role": 3, "gold_per_min": 250},  # pos 5 (lower GPM support)
        ]

        assign_positions(players)

        pos4 = next(p for p in players if p["position"] == 4)
        pos5 = next(p for p in players if p["position"] == 5)

        assert pos4["role"] == "support"
        assert pos5["role"] == "support"
        assert pos4["gold_per_min"] > pos5["gold_per_min"]

    def test_both_teams_get_positions(self):
        """Both radiant (slot < 128) and dire (slot >= 128) should get positions."""
        players = [
            # Radiant
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 600},
            {"player_slot": 1, "lane_role": 2, "gold_per_min": 550},
            {"player_slot": 2, "lane_role": 3, "gold_per_min": 450},
            {"player_slot": 3, "lane_role": 1, "gold_per_min": 250},
            {"player_slot": 4, "lane_role": 3, "gold_per_min": 300},
            # Dire
            {"player_slot": 128, "lane_role": 1, "gold_per_min": 620},
            {"player_slot": 129, "lane_role": 2, "gold_per_min": 570},
            {"player_slot": 130, "lane_role": 3, "gold_per_min": 460},
            {"player_slot": 131, "lane_role": 1, "gold_per_min": 260},
            {"player_slot": 132, "lane_role": 3, "gold_per_min": 310},
        ]

        assign_positions(players)

        radiant = [p for p in players if p["player_slot"] < 128]
        dire = [p for p in players if p["player_slot"] >= 128]

        radiant_positions = sorted([p["position"] for p in radiant])
        dire_positions = sorted([p["position"] for p in dire])

        assert radiant_positions == [1, 2, 3, 4, 5]
        assert dire_positions == [1, 2, 3, 4, 5]

    def test_jungle_player_becomes_support(self):
        """Player with lane_role=None (jungle/roaming) should become support."""
        players = [
            {"player_slot": 0, "lane_role": 1, "gold_per_min": 600},
            {"player_slot": 1, "lane_role": 2, "gold_per_min": 550},
            {"player_slot": 2, "lane_role": 3, "gold_per_min": 450},
            {"player_slot": 3, "lane_role": 1, "gold_per_min": 250},
            {"player_slot": 4, "lane_role": None, "gold_per_min": 320},  # roaming
        ]

        assign_positions(players)

        roamer = next(p for p in players if p["lane_role"] is None)
        assert roamer["role"] == "support"
        assert roamer["position"] in [4, 5]


class TestGetLaneName:
    """Tests for get_lane_name function."""

    def test_mid_lane_same_for_both_teams(self):
        """Mid lane is the same for both teams."""
        assert get_lane_name(2, is_radiant=True) == "mid_lane"
        assert get_lane_name(2, is_radiant=False) == "mid_lane"

    def test_jungle_same_for_both_teams(self):
        """Jungle is the same for both teams."""
        assert get_lane_name(4, is_radiant=True) == "jungle"
        assert get_lane_name(4, is_radiant=False) == "jungle"

    def test_radiant_bottom_is_safe_lane(self):
        """Radiant bottom lane (1) is safe lane."""
        assert get_lane_name(1, is_radiant=True) == "safe_lane"

    def test_radiant_top_is_off_lane(self):
        """Radiant top lane (3) is off lane."""
        assert get_lane_name(3, is_radiant=True) == "off_lane"

    def test_dire_top_is_safe_lane(self):
        """Dire top lane (3) is safe lane."""
        assert get_lane_name(3, is_radiant=False) == "safe_lane"

    def test_dire_bottom_is_off_lane(self):
        """Dire bottom lane (1) is off lane."""
        assert get_lane_name(1, is_radiant=False) == "off_lane"

    def test_unknown_lane_returns_none(self):
        """Unknown lane values return None."""
        assert get_lane_name(5, is_radiant=True) is None
        assert get_lane_name(0, is_radiant=False) is None


class TestPositionFieldInModels:
    """Tests for position field in Pydantic models."""

    def test_hero_stats_accepts_position(self):
        """HeroStats should accept position field."""
        hero = HeroStats(
            hero_id=2,
            hero_name="npc_dota_hero_axe",
            localized_name="Axe",
            team="radiant",
            position=3,
            kills=5,
            deaths=2,
            assists=10,
            last_hits=150,
            denies=10,
            gpm=450,
            xpm=500,
            net_worth=15000,
            hero_damage=20000,
            tower_damage=1000,
            hero_healing=0,
            lane="off_lane",
            role="core",
            items=[],
        )
        assert hero.position == 3

    def test_hero_stats_position_defaults_to_none(self):
        """HeroStats position should default to None."""
        hero = HeroStats(
            hero_id=2,
            hero_name="npc_dota_hero_axe",
            localized_name="Axe",
            team="radiant",
            kills=0,
            deaths=0,
            assists=0,
            last_hits=0,
            denies=0,
            gpm=0,
            xpm=0,
            net_worth=0,
            hero_damage=0,
            tower_damage=0,
            hero_healing=0,
            items=[],
        )
        assert hero.position is None

    def test_match_player_info_accepts_position(self):
        """MatchPlayerInfo should accept position field."""
        player = MatchPlayerInfo(
            player_name="TestPlayer",
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            position=1,
        )
        assert player.position == 1

    def test_match_player_info_position_defaults_to_none(self):
        """MatchPlayerInfo position should default to None."""
        player = MatchPlayerInfo(
            player_name="TestPlayer",
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
        )
        assert player.position is None


class TestDraftActionWithContext:
    """Tests for DraftAction model with counters and matchup data."""

    def test_draft_action_accepts_position(self):
        """DraftAction should accept position for picks."""
        action = DraftAction(
            order=10,
            is_pick=True,
            team="radiant",
            hero_id=2,
            hero_name="axe",
            localized_name="Axe",
            position=3,
        )
        assert action.position == 3

    def test_draft_action_position_none_for_bans(self):
        """DraftAction position should typically be None for bans."""
        action = DraftAction(
            order=1,
            is_pick=False,
            team="dire",
            hero_id=23,
            hero_name="kunkka",
            localized_name="Kunkka",
            position=None,
        )
        assert action.position is None

    def test_draft_action_accepts_counters(self):
        """DraftAction should accept counters list."""
        counters = [
            HeroMatchupInfo(hero_id=6, localized_name="Doom", reason="Doom disables abilities"),
            HeroMatchupInfo(hero_id=74, localized_name="Invoker", reason="EMP drains mana"),
        ]
        action = DraftAction(
            order=10,
            is_pick=True,
            team="radiant",
            hero_id=1,
            hero_name="antimage",
            localized_name="Anti-Mage",
            counters=counters,
        )
        assert len(action.counters) == 2
        assert action.counters[0].localized_name == "Doom"

    def test_draft_action_accepts_good_against(self):
        """DraftAction should accept good_against list."""
        good_against = [
            HeroMatchupInfo(hero_id=94, localized_name="Medusa", reason="Mana Break is effective"),
        ]
        action = DraftAction(
            order=10,
            is_pick=True,
            team="radiant",
            hero_id=1,
            hero_name="antimage",
            localized_name="Anti-Mage",
            good_against=good_against,
        )
        assert len(action.good_against) == 1
        assert action.good_against[0].reason == "Mana Break is effective"

    def test_draft_action_accepts_when_to_pick(self):
        """DraftAction should accept when_to_pick list."""
        action = DraftAction(
            order=10,
            is_pick=True,
            team="radiant",
            hero_id=1,
            hero_name="antimage",
            localized_name="Anti-Mage",
            when_to_pick=["Enemy has mana-dependent heroes", "Team can hold 4v5"],
        )
        assert len(action.when_to_pick) == 2
        assert "mana-dependent" in action.when_to_pick[0]

    def test_draft_action_defaults_empty_lists(self):
        """DraftAction should default counters/good_against/when_to_pick to empty lists."""
        action = DraftAction(
            order=1,
            is_pick=True,
            team="radiant",
            hero_id=1,
            hero_name="antimage",
            localized_name="Anti-Mage",
        )
        assert action.counters == []
        assert action.good_against == []
        assert action.when_to_pick == []


class TestHeroMatchupInfo:
    """Tests for HeroMatchupInfo model."""

    def test_hero_matchup_info_creation(self):
        """HeroMatchupInfo should accept all required fields."""
        matchup = HeroMatchupInfo(
            hero_id=6,
            localized_name="Doom",
            reason="Doom disables all abilities and items",
        )
        assert matchup.hero_id == 6
        assert matchup.localized_name == "Doom"
        assert "abilities" in matchup.reason
