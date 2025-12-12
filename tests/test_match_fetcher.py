"""Tests for match_fetcher module using real match data from 8461956309."""

from src.utils.match_fetcher import get_lane_name


class TestGetLaneNameWithRealData:
    """Tests for get_lane_name function verified against real match 8461956309.

    Match 8461956309 (TI Grand Final) lane assignments:
    - Radiant: Ame (lane 1), Xm (lane 2), Xxs (lane 3), XinQ (lane 3), xNova (lane 1)
    - Dire: Sneyking (lane 3), skiter (lane 3), Malr1ne (lane 2), AMMAR (lane 1), Cr1t (lane 1)
    """

    def test_radiant_bottom_is_safe_lane(self, match_players):
        """Ame (Radiant, lane 1) plays safe lane - verified from match."""
        ame = next(p for p in match_players if p.get("pro_name") == "Ame")
        assert ame["lane"] == 1
        assert ame["team"] == "radiant"
        assert get_lane_name(ame["lane"], is_radiant=True) == "safe_lane"
        assert ame["lane_name"] == "safe_lane"

    def test_radiant_top_is_off_lane(self, match_players):
        """Xxs (Radiant, lane 3) plays off lane - verified from match."""
        xxs = next(p for p in match_players if p.get("pro_name") == "Xxs")
        assert xxs["lane"] == 3
        assert xxs["team"] == "radiant"
        assert get_lane_name(xxs["lane"], is_radiant=True) == "off_lane"
        assert xxs["lane_name"] == "off_lane"

    def test_dire_top_is_safe_lane(self, match_players):
        """Skiter (Dire, lane 3) plays safe lane - verified from match."""
        skiter = next(p for p in match_players if p.get("pro_name") == "skiter")
        assert skiter["lane"] == 3
        assert skiter["team"] == "dire"
        assert get_lane_name(skiter["lane"], is_radiant=False) == "safe_lane"
        assert skiter["lane_name"] == "safe_lane"

    def test_dire_bottom_is_off_lane(self, match_players):
        """AMMAR (Dire, lane 1) plays off lane - verified from match."""
        ammar = next(p for p in match_players if "AMMAR" in (p.get("pro_name") or ""))
        assert ammar["lane"] == 1
        assert ammar["team"] == "dire"
        assert get_lane_name(ammar["lane"], is_radiant=False) == "off_lane"
        assert ammar["lane_name"] == "off_lane"

    def test_mid_lane_radiant(self, match_players):
        """Xm (Radiant, lane 2) plays mid - verified from match."""
        xm = next(p for p in match_players if p.get("pro_name") == "Xm")
        assert xm["lane"] == 2
        assert xm["team"] == "radiant"
        assert get_lane_name(xm["lane"], is_radiant=True) == "mid_lane"
        assert xm["lane_name"] == "mid_lane"

    def test_mid_lane_dire(self, match_players):
        """Malr1ne (Dire, lane 2) plays mid - verified from match."""
        malr1ne = next(p for p in match_players if p.get("pro_name") == "Malr1ne")
        assert malr1ne["lane"] == 2
        assert malr1ne["team"] == "dire"
        assert get_lane_name(malr1ne["lane"], is_radiant=False) == "mid_lane"
        assert malr1ne["lane_name"] == "mid_lane"

    def test_jungle_returns_jungle(self):
        """Lane 4 returns jungle for both teams."""
        assert get_lane_name(4, is_radiant=True) == "jungle"
        assert get_lane_name(4, is_radiant=False) == "jungle"

    def test_unknown_lane_returns_none(self):
        """Invalid lane values return None."""
        assert get_lane_name(0, is_radiant=True) is None
        assert get_lane_name(5, is_radiant=False) is None
        assert get_lane_name(99, is_radiant=True) is None


class TestMatchPlayersData:
    """Tests for match player data from OpenDota API."""

    def test_match_has_10_players(self, match_players):
        """Match 8461956309 has 10 players."""
        assert len(match_players) == 10

    def test_radiant_has_5_players(self, match_players):
        """Match has 5 Radiant players."""
        radiant = [p for p in match_players if p["team"] == "radiant"]
        assert len(radiant) == 5

    def test_dire_has_5_players(self, match_players):
        """Match has 5 Dire players."""
        dire = [p for p in match_players if p["team"] == "dire"]
        assert len(dire) == 5

    def test_all_players_have_lane_data(self, match_players):
        """All players have lane assignment."""
        for player in match_players:
            assert player.get("lane") is not None
            assert player.get("lane_name") is not None

    def test_ame_is_position_1_juggernaut(self, match_players):
        """Ame plays Juggernaut (hero_id=8) as position 1."""
        ame = next(p for p in match_players if p.get("pro_name") == "Ame")
        assert ame["hero_id"] == 8  # Juggernaut
        assert ame["position"] == 1
        assert ame["role"] == "core"

    def test_skiter_is_position_1_medusa(self, match_players):
        """Skiter plays Medusa (hero_id=94) as position 1."""
        skiter = next(p for p in match_players if p.get("pro_name") == "skiter")
        assert skiter["hero_id"] == 94  # Medusa
        assert skiter["position"] == 1
        assert skiter["role"] == "core"
