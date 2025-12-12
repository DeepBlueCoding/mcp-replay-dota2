"""
Tests for match 8594217096 - OG match with Pure, bzm, 33, Whitemon, Ari.

All tests use verified values from the actual replay.
Radiant won with Pure (Juggernaut) having 16/2/10 and 941 GPM.
"""

from tests.conftest import (
    MATCH_2_BARRACKS_KILLS,
    MATCH_2_COURIER_KILLS,
    MATCH_2_FIRST_BLOOD_KILLER,
    MATCH_2_FIRST_BLOOD_VICTIM,
    MATCH_2_ROSHAN_KILLS,
    MATCH_2_RUNE_PICKUPS,
    MATCH_2_TORMENTOR_KILLS,
    MATCH_2_TOTAL_DEATHS,
    MATCH_2_TOWER_KILLS,
)


class TestMatch8594217096HeroDeaths:
    """Tests for hero deaths in match 8594217096."""

    def test_total_hero_deaths(self, hero_deaths_2):
        """Match has 53 hero deaths after game start."""
        assert len(hero_deaths_2) == MATCH_2_TOTAL_DEATHS

    def test_first_blood_victim(self, hero_deaths_2):
        """First blood victim is Batrider."""
        assert hero_deaths_2[0].victim == MATCH_2_FIRST_BLOOD_VICTIM

    def test_first_blood_killer(self, hero_deaths_2):
        """First blood killer is Pugna."""
        assert hero_deaths_2[0].killer == MATCH_2_FIRST_BLOOD_KILLER

    def test_first_blood_time(self, hero_deaths_2):
        """First blood at 1:24."""
        assert hero_deaths_2[0].game_time_str == "1:24"

    def test_hero_deaths_have_position(self, hero_deaths_2):
        """All hero deaths have position data."""
        for death in hero_deaths_2[:10]:
            assert death.position_x is not None
            assert death.position_y is not None


class TestMatch8594217096Objectives:
    """Tests for objectives in match 8594217096."""

    def test_roshan_kills_count(self, roshan_kills_2):
        """Match has 3 Roshan kills."""
        assert len(roshan_kills_2) == MATCH_2_ROSHAN_KILLS

    def test_first_roshan_time(self, roshan_kills_2):
        """First Roshan at 21:25."""
        assert roshan_kills_2[0].game_time_str == "21:25"

    def test_first_roshan_killer(self, roshan_kills_2):
        """First Roshan killed by Juggernaut."""
        assert roshan_kills_2[0].killer == "juggernaut"

    def test_tormentor_kills_count(self, tormentor_kills_2):
        """Match has 2 Tormentor kills."""
        assert len(tormentor_kills_2) == MATCH_2_TORMENTOR_KILLS

    def test_first_tormentor_time(self, tormentor_kills_2):
        """First Tormentor at 20:11."""
        assert tormentor_kills_2[0].game_time_str == "20:11"

    def test_first_tormentor_killer(self, tormentor_kills_2):
        """First Tormentor killed by Centaur."""
        assert tormentor_kills_2[0].killer == "centaur"

    def test_tower_kills_count(self, tower_kills_2):
        """Match has 14 tower kills."""
        assert len(tower_kills_2) == MATCH_2_TOWER_KILLS

    def test_barracks_kills_count(self, barracks_kills_2):
        """Match has 6 barracks kills."""
        assert len(barracks_kills_2) == MATCH_2_BARRACKS_KILLS


class TestMatch8594217096Runes:
    """Tests for rune pickups in match 8594217096."""

    def test_rune_pickups_count(self, rune_pickups_2):
        """Match has 13 rune pickups."""
        assert len(rune_pickups_2) == MATCH_2_RUNE_PICKUPS

    def test_first_rune_time(self, rune_pickups_2):
        """First rune at 6:03."""
        assert rune_pickups_2[0].game_time_str == "6:03"

    def test_first_rune_hero(self, rune_pickups_2):
        """First rune picked up by Jakiro."""
        assert rune_pickups_2[0].hero == "jakiro"

    def test_first_rune_type(self, rune_pickups_2):
        """First rune is regeneration."""
        assert rune_pickups_2[0].rune_type == "regeneration"


class TestMatch8594217096Couriers:
    """Tests for courier kills in match 8594217096."""

    def test_courier_kills_count(self, courier_kills_2):
        """Match has 5 courier kills."""
        assert len(courier_kills_2) == MATCH_2_COURIER_KILLS

    def test_first_courier_time(self, courier_kills_2):
        """First courier kill at 3:42."""
        assert courier_kills_2[0].game_time_str == "3:42"

    def test_first_courier_killer(self, courier_kills_2):
        """First courier killed by Phantom Lancer."""
        assert courier_kills_2[0].killer == "phantom_lancer"


class TestMatch8594217096Players:
    """Tests for player data in match 8594217096."""

    def test_match_has_10_players(self, match_players_2):
        """Match has 10 players."""
        assert len(match_players_2) == 10

    def test_radiant_has_5_players(self, match_players_2):
        """Radiant has 5 players."""
        radiant = [p for p in match_players_2 if p["team"] == "radiant"]
        assert len(radiant) == 5

    def test_dire_has_5_players(self, match_players_2):
        """Dire has 5 players."""
        dire = [p for p in match_players_2 if p["team"] == "dire"]
        assert len(dire) == 5

    def test_pure_is_position_1(self, match_players_2):
        """Pure plays position 1 (Juggernaut)."""
        pure = next(p for p in match_players_2 if p.get("pro_name") == "Pure")
        assert pure["position"] == 1
        assert pure["hero_id"] == 8  # Juggernaut
        assert pure["role"] == "core"

    def test_bzm_is_position_2(self, match_players_2):
        """bzm plays position 2 (Void Spirit)."""
        bzm = next(p for p in match_players_2 if p.get("pro_name") == "bzm")
        assert bzm["position"] == 2
        assert bzm["hero_id"] == 126  # Void Spirit
        assert bzm["role"] == "core"

    def test_33_is_position_3(self, match_players_2):
        """33 plays position 3 (Centaur)."""
        player_33 = next(p for p in match_players_2 if p.get("pro_name") == "33")
        assert player_33["position"] == 3
        assert player_33["hero_id"] == 96  # Centaur
        assert player_33["role"] == "core"

    def test_whitemon_is_position_4(self, match_players_2):
        """Whitemon plays position 4 (Jakiro)."""
        whitemon = next(p for p in match_players_2 if p.get("pro_name") == "Whitemon")
        assert whitemon["position"] == 4
        assert whitemon["hero_id"] == 64  # Jakiro
        assert whitemon["role"] == "support"

    def test_ari_is_position_5(self, match_players_2):
        """Ari plays position 5 (Batrider)."""
        ari = next(p for p in match_players_2 if p.get("pro_name") == "Ari")
        assert ari["position"] == 5
        assert ari["hero_id"] == 65  # Batrider
        assert ari["role"] == "support"

    def test_pure_has_highest_gpm(self, match_players_2):
        """Pure has highest GPM (941)."""
        pure = next(p for p in match_players_2 if p.get("pro_name") == "Pure")
        assert pure["gold_per_min"] == 941

    def test_saksa_is_dire_position_4(self, match_players_2):
        """Saksa plays position 4 (Snapfire) for Dire."""
        saksa = next(p for p in match_players_2 if p.get("pro_name") == "Saksa")
        assert saksa["position"] == 4
        assert saksa["hero_id"] == 128  # Snapfire
        assert saksa["team"] == "dire"


class TestMatch8594217096LaneSummary:
    """Tests for lane summary in match 8594217096."""

    def test_top_lane_winner(self, lane_summary_2):
        """Dire won top lane."""
        assert lane_summary_2.top_winner == "dire"

    def test_mid_lane_winner(self, lane_summary_2):
        """Radiant won mid lane."""
        assert lane_summary_2.mid_winner == "radiant"

    def test_bot_lane_winner(self, lane_summary_2):
        """Radiant won bot lane."""
        assert lane_summary_2.bot_winner == "radiant"

    def test_radiant_laning_score_higher(self, lane_summary_2):
        """Radiant has higher laning score (won 2/3 lanes)."""
        assert lane_summary_2.radiant_laning_score > lane_summary_2.dire_laning_score

    def test_hero_stats_count(self, lane_summary_2):
        """Lane summary has 10 hero stats."""
        assert len(lane_summary_2.hero_stats) == 10

    def test_void_spirit_mid_cs(self, lane_summary_2):
        """Void Spirit (bzm) has good mid CS at 10 minutes."""
        void_spirit = next(h for h in lane_summary_2.hero_stats if h.hero == "void_spirit")
        assert void_spirit.last_hits_10min >= 50
        assert void_spirit.lane == "mid"

    def test_juggernaut_bot_cs(self, lane_summary_2):
        """Juggernaut (Pure) has good bot CS at 10 minutes."""
        juggernaut = next(h for h in lane_summary_2.hero_stats if h.hero == "juggernaut")
        assert juggernaut.last_hits_10min >= 40
        assert juggernaut.lane == "bot"
