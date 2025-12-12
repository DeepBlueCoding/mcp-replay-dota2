"""
Tests for the FarmingService using real replay data.

All tests use data from match 8461956309 with verified values.
"""

from src.services.models.farming_data import FarmingPatternResponse


class TestMedusaFarmingPattern:
    """Tests for Medusa's farming pattern in match 8461956309."""

    def test_medusa_total_lane_creeps(self, medusa_farming_pattern):
        """Medusa killed 97 lane creeps in 0-15 minutes."""
        assert medusa_farming_pattern.summary.total_lane_creeps == 97

    def test_medusa_total_neutral_creeps(self, medusa_farming_pattern):
        """Medusa killed 48 neutral creeps in 0-15 minutes."""
        assert medusa_farming_pattern.summary.total_neutral_creeps == 48

    def test_medusa_jungle_percentage(self, medusa_farming_pattern):
        """Medusa's jungle percentage is ~33%."""
        assert 30 <= medusa_farming_pattern.summary.jungle_percentage <= 36

    def test_medusa_creep_kills_count(self, medusa_farming_pattern):
        """Medusa has 177 creep kills recorded."""
        assert len(medusa_farming_pattern.creep_kills) == 177

    def test_medusa_first_creep_kill(self, medusa_farming_pattern):
        """First creep kill at 0:46 is a lane creep."""
        first_creep = medusa_farming_pattern.creep_kills[0]
        assert first_creep.game_time_str == "0:46"
        assert first_creep.creep_type == "lane"
        assert "goodguys_melee" in first_creep.creep_name

    def test_medusa_camps_cleared_includes_large_camps(self, medusa_farming_pattern):
        """Medusa cleared large camps (centaur, troll, satyr)."""
        camps = medusa_farming_pattern.summary.camps_cleared
        assert "large_troll" in camps
        assert camps["large_troll"] >= 1

    def test_medusa_farming_pattern_response_type(self, medusa_farming_pattern):
        """Farming pattern returns correct response model."""
        assert isinstance(medusa_farming_pattern, FarmingPatternResponse)
        assert medusa_farming_pattern.success is True
        assert medusa_farming_pattern.hero == "medusa"

    def test_medusa_has_per_minute_data(self, medusa_farming_pattern):
        """Farming pattern includes per-minute breakdown."""
        assert len(medusa_farming_pattern.minutes) > 0
        minute_5 = next((m for m in medusa_farming_pattern.minutes if m.minute == 5), None)
        assert minute_5 is not None


class TestJuggernautFarmingPattern:
    """Tests for Juggernaut's farming pattern in match 8461956309."""

    def test_juggernaut_total_lane_creeps(self, juggernaut_farming_pattern):
        """Juggernaut killed 80 lane creeps in 0-15 minutes."""
        assert juggernaut_farming_pattern.summary.total_lane_creeps == 80

    def test_juggernaut_total_neutral_creeps(self, juggernaut_farming_pattern):
        """Juggernaut killed 24 neutral creeps in 0-15 minutes."""
        assert juggernaut_farming_pattern.summary.total_neutral_creeps == 24

    def test_juggernaut_farms_less_jungle_than_medusa(self, juggernaut_farming_pattern, medusa_farming_pattern):
        """Juggernaut farms less jungle than Medusa."""
        jug_jungle = juggernaut_farming_pattern.summary.jungle_percentage
        med_jungle = medusa_farming_pattern.summary.jungle_percentage
        assert jug_jungle < med_jungle


class TestCreepClassification:
    """Tests for creep classification using real data."""

    def test_lane_creeps_have_correct_type(self, medusa_farming_pattern):
        """Lane creeps are classified as 'lane' type."""
        lane_creeps = [c for c in medusa_farming_pattern.creep_kills if c.creep_type == "lane"]
        assert len(lane_creeps) == 97
        for creep in lane_creeps[:5]:
            assert "creep_goodguys" in creep.creep_name or "creep_badguys" in creep.creep_name

    def test_neutral_creeps_have_correct_type(self, medusa_farming_pattern):
        """Neutral creeps are classified as 'neutral' type."""
        neutral_creeps = [c for c in medusa_farming_pattern.creep_kills if c.creep_type == "neutral"]
        assert len(neutral_creeps) >= 48
        for creep in neutral_creeps[:5]:
            assert "neutral" in creep.creep_name

    def test_creep_kills_have_game_time(self, medusa_farming_pattern):
        """All creep kills have valid game time."""
        for creep in medusa_farming_pattern.creep_kills:
            assert creep.game_time >= 0
            assert creep.game_time_str is not None


class TestLaneSummary:
    """Tests for lane summary using real replay data."""

    def test_lane_winners(self, lane_summary):
        """Lane winners are correctly identified."""
        assert lane_summary.top_winner == "dire"
        assert lane_summary.mid_winner == "radiant"
        assert lane_summary.bot_winner == "radiant"

    def test_laning_scores(self, lane_summary):
        """Laning scores are calculated."""
        assert lane_summary.radiant_laning_score > 200
        assert lane_summary.dire_laning_score > 200

    def test_hero_stats_present(self, lane_summary):
        """Hero stats are included for all heroes."""
        assert len(lane_summary.hero_stats) == 10


class TestCSAtMinute:
    """Tests for CS at specific minute using real replay data."""

    def test_cs_at_10_has_all_heroes(self, cs_at_10_minutes):
        """CS data at 10 minutes includes all 10 heroes."""
        assert len(cs_at_10_minutes) == 10

    def test_cs_at_10_medusa_has_good_cs(self, cs_at_10_minutes):
        """Medusa has decent CS at 10 minutes."""
        medusa_cs = cs_at_10_minutes.get("medusa", {})
        assert medusa_cs.get("last_hits", 0) >= 50

    def test_cs_values_are_integers(self, cs_at_10_minutes):
        """CS values are integers."""
        for hero, stats in cs_at_10_minutes.items():
            assert isinstance(stats.get("last_hits", 0), int)
            assert isinstance(stats.get("denies", 0), int)
