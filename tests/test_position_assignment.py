"""Tests for position (1-5) assignment logic using real match data from 8461956309."""

from src.models.match_info import DraftAction, HeroMatchupInfo
from src.models.tool_responses import HeroStats, MatchPlayerInfo


class TestAssignPositionsWithRealData:
    """Tests for position assignment verified against real match 8461956309.

    Radiant positions (verified from OpenDota):
    - Ame (pos 1, core) - lane_role=1, gpm=769
    - Xm (pos 2, core) - lane_role=2, gpm=582
    - Xxs (pos 3, core) - lane_role=3, gpm=515
    - XinQ (pos 4, support) - lane_role=3, gpm=316
    - xNova (pos 5, support) - lane_role=1, gpm=214

    Dire positions (verified from OpenDota):
    - skiter (pos 1, core) - lane_role=1, gpm=1000
    - Malr1ne (pos 2, core) - lane_role=2, gpm=578
    - AMMAR (pos 3, core) - lane_role=3, gpm=576
    - Sneyking (pos 4, support) - lane_role=1, gpm=492
    - Cr1t (pos 5, support) - lane_role=3, gpm=335
    """

    def test_all_positions_assigned_for_radiant(self, match_players):
        """Radiant has all 5 positions assigned."""
        radiant = [p for p in match_players if p["team"] == "radiant"]
        positions = sorted([p["position"] for p in radiant])
        assert positions == [1, 2, 3, 4, 5]

    def test_all_positions_assigned_for_dire(self, match_players):
        """Dire has all 5 positions assigned."""
        dire = [p for p in match_players if p["team"] == "dire"]
        positions = sorted([p["position"] for p in dire])
        assert positions == [1, 2, 3, 4, 5]

    def test_ame_is_radiant_position_1(self, match_players):
        """Ame (highest GPM safelane) is position 1 core."""
        ame = next(p for p in match_players if p.get("pro_name") == "Ame")
        assert ame["position"] == 1
        assert ame["role"] == "core"
        assert ame["lane_role"] == 1  # safelane

    def test_xm_is_radiant_position_2(self, match_players):
        """Xm (mid lane) is position 2 core."""
        xm = next(p for p in match_players if p.get("pro_name") == "Xm")
        assert xm["position"] == 2
        assert xm["role"] == "core"
        assert xm["lane_role"] == 2  # mid

    def test_xxs_is_radiant_position_3(self, match_players):
        """Xxs (highest GPM offlane) is position 3 core."""
        xxs = next(p for p in match_players if p.get("pro_name") == "Xxs")
        assert xxs["position"] == 3
        assert xxs["role"] == "core"
        assert xxs["lane_role"] == 3  # offlane

    def test_xinq_is_radiant_position_4(self, match_players):
        """XinQ (higher GPM support) is position 4."""
        xinq = next(p for p in match_players if p.get("pro_name") == "XinQ")
        assert xinq["position"] == 4
        assert xinq["role"] == "support"

    def test_xnova_is_radiant_position_5(self, match_players):
        """xNova (lowest GPM support) is position 5."""
        xnova = next(p for p in match_players if p.get("pro_name") == "xNova")
        assert xnova["position"] == 5
        assert xnova["role"] == "support"

    def test_skiter_is_dire_position_1(self, match_players):
        """Skiter (highest GPM) is position 1 core."""
        skiter = next(p for p in match_players if p.get("pro_name") == "skiter")
        assert skiter["position"] == 1
        assert skiter["role"] == "core"
        assert skiter["gold_per_min"] == 1000  # Highest GPM in match

    def test_malr1ne_is_dire_position_2(self, match_players):
        """Malr1ne (mid lane) is position 2 core."""
        malr1ne = next(p for p in match_players if p.get("pro_name") == "Malr1ne")
        assert malr1ne["position"] == 2
        assert malr1ne["role"] == "core"
        assert malr1ne["lane_role"] == 2

    def test_ammar_is_dire_position_3(self, match_players):
        """AMMAR (offlane core) is position 3."""
        ammar = next(p for p in match_players if "AMMAR" in (p.get("pro_name") or ""))
        assert ammar["position"] == 3
        assert ammar["role"] == "core"
        assert ammar["lane_role"] == 3

    def test_supports_have_lower_gpm_than_cores(self, match_players):
        """Supports (pos 4-5) have lower GPM than cores (pos 1-3)."""
        radiant = [p for p in match_players if p["team"] == "radiant"]
        radiant_cores = [p for p in radiant if p["position"] <= 3]
        radiant_supports = [p for p in radiant if p["position"] >= 4]

        min_core_gpm = min(p["gold_per_min"] for p in radiant_cores)
        max_support_gpm = max(p["gold_per_min"] for p in radiant_supports)

        assert max_support_gpm < min_core_gpm

    def test_pos4_has_higher_gpm_than_pos5(self, match_players):
        """Position 4 support has higher GPM than position 5."""
        radiant = [p for p in match_players if p["team"] == "radiant"]
        pos4 = next(p for p in radiant if p["position"] == 4)
        pos5 = next(p for p in radiant if p["position"] == 5)

        assert pos4["gold_per_min"] > pos5["gold_per_min"]


class TestPositionFieldInModelsWithRealData:
    """Tests for position field in models using real match 8461956309 data."""

    def test_hero_stats_with_ame_data(self, match_players):
        """HeroStats model with Ame's real data from match."""
        ame = next(p for p in match_players if p.get("pro_name") == "Ame")
        hero = HeroStats(
            hero_id=ame["hero_id"],
            hero_name="npc_dota_hero_juggernaut",
            localized_name="Juggernaut",
            team=ame["team"],
            position=ame["position"],
            kills=ame["kills"],
            deaths=ame["deaths"],
            assists=ame["assists"],
            last_hits=ame["last_hits"],
            denies=ame["denies"],
            gpm=ame["gold_per_min"],
            xpm=ame["xp_per_min"],
            net_worth=ame["net_worth"],
            hero_damage=ame["hero_damage"],
            tower_damage=ame["tower_damage"],
            hero_healing=ame["hero_healing"],
            lane=ame["lane_name"],
            role=ame["role"],
            items=[],
        )
        assert hero.position == 1
        assert hero.hero_id == 8  # Juggernaut
        assert hero.gpm == 769
        assert hero.role == "core"

    def test_hero_stats_with_xnova_support_data(self, match_players):
        """HeroStats model with xNova's support data from match."""
        xnova = next(p for p in match_players if p.get("pro_name") == "xNova")
        hero = HeroStats(
            hero_id=xnova["hero_id"],
            hero_name="npc_dota_hero_pugna",
            localized_name="Pugna",
            team=xnova["team"],
            position=xnova["position"],
            kills=xnova["kills"],
            deaths=xnova["deaths"],
            assists=xnova["assists"],
            last_hits=xnova["last_hits"],
            denies=xnova["denies"],
            gpm=xnova["gold_per_min"],
            xpm=xnova["xp_per_min"],
            net_worth=xnova["net_worth"],
            hero_damage=xnova["hero_damage"],
            tower_damage=xnova["tower_damage"],
            hero_healing=xnova["hero_healing"],
            lane=xnova["lane_name"],
            role=xnova["role"],
            items=[],
        )
        assert hero.position == 5
        assert hero.hero_id == 45  # Pugna
        assert hero.role == "support"

    def test_match_player_info_with_skiter_data(self, match_players):
        """MatchPlayerInfo model with skiter's data from match."""
        skiter = next(p for p in match_players if p.get("pro_name") == "skiter")
        player = MatchPlayerInfo(
            player_name=skiter["pro_name"],
            hero_id=skiter["hero_id"],
            hero_name="npc_dota_hero_medusa",
            localized_name="Medusa",
            position=skiter["position"],
        )
        assert player.position == 1
        assert player.hero_id == 94  # Medusa
        assert player.player_name == "skiter"

    def test_match_player_info_position_defaults_to_none(self):
        """MatchPlayerInfo position should default to None."""
        player = MatchPlayerInfo(
            player_name="TestPlayer",
            hero_id=94,
            hero_name="npc_dota_hero_medusa",
            localized_name="Medusa",
        )
        assert player.position is None


class TestDraftActionWithRealData:
    """Tests for DraftAction model using real match context."""

    def test_draft_action_juggernaut_pick(self, match_players):
        """DraftAction for Juggernaut (Ame's pick) from match 8461956309."""
        ame = next(p for p in match_players if p.get("pro_name") == "Ame")
        action = DraftAction(
            order=10,
            is_pick=True,
            team="radiant",
            hero_id=ame["hero_id"],
            hero_name="juggernaut",
            localized_name="Juggernaut",
            position=ame["position"],
        )
        assert action.hero_id == 8
        assert action.position == 1
        assert action.team == "radiant"

    def test_draft_action_medusa_pick(self, match_players):
        """DraftAction for Medusa (skiter's pick) from match 8461956309."""
        skiter = next(p for p in match_players if p.get("pro_name") == "skiter")
        action = DraftAction(
            order=12,
            is_pick=True,
            team="dire",
            hero_id=skiter["hero_id"],
            hero_name="medusa",
            localized_name="Medusa",
            position=skiter["position"],
        )
        assert action.hero_id == 94
        assert action.position == 1
        assert action.team == "dire"

    def test_draft_action_ban(self):
        """DraftAction for a ban (position should be None)."""
        action = DraftAction(
            order=1,
            is_pick=False,
            team="dire",
            hero_id=23,
            hero_name="kunkka",
            localized_name="Kunkka",
            position=None,
        )
        assert action.is_pick is False
        assert action.position is None

    def test_draft_action_with_matchup_context(self):
        """DraftAction with counters/good_against for Juggernaut."""
        counters = [
            HeroMatchupInfo(hero_id=94, localized_name="Medusa", reason="Split Shot farms faster"),
        ]
        good_against = [
            HeroMatchupInfo(hero_id=89, localized_name="Naga Siren", reason="Blade Fury dispels Net"),
        ]
        action = DraftAction(
            order=10,
            is_pick=True,
            team="radiant",
            hero_id=8,
            hero_name="juggernaut",
            localized_name="Juggernaut",
            position=1,
            counters=counters,
            good_against=good_against,
        )
        assert len(action.counters) == 1
        assert action.counters[0].hero_id == 94
        assert len(action.good_against) == 1
        assert action.good_against[0].hero_id == 89

    def test_draft_action_defaults_empty_lists(self):
        """DraftAction defaults counters/good_against to empty lists."""
        action = DraftAction(
            order=1,
            is_pick=True,
            team="radiant",
            hero_id=8,
            hero_name="juggernaut",
            localized_name="Juggernaut",
        )
        assert action.counters == []
        assert action.good_against == []
        assert action.when_to_pick == []


class TestHeroMatchupInfoWithRealData:
    """Tests for HeroMatchupInfo using real match context."""

    def test_medusa_vs_juggernaut_matchup(self):
        """HeroMatchupInfo for Medusa vs Juggernaut (match 8461956309 matchup)."""
        matchup = HeroMatchupInfo(
            hero_id=94,
            localized_name="Medusa",
            reason="Split Shot clears Healing Ward, Stone Gaze counters Omnislash",
        )
        assert matchup.hero_id == 94
        assert matchup.localized_name == "Medusa"
        assert "Omnislash" in matchup.reason

    def test_naga_siren_counter_matchup(self):
        """HeroMatchupInfo for Naga Siren (match 8461956309 hero)."""
        matchup = HeroMatchupInfo(
            hero_id=89,
            localized_name="Naga Siren",
            reason="Song of the Siren provides team reset",
        )
        assert matchup.hero_id == 89
        assert "Song" in matchup.reason
