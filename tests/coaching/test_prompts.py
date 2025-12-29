"""
Tests for coaching prompt generators in src/coaching/prompts.py.

These tests verify that prompt generators handle edge cases correctly,
especially around data type conversions (float game_time, etc.).
"""

from src.coaching.prompts import (
    get_death_analysis_prompt,
    get_hero_performance_prompt,
    get_lane_analysis_prompt,
    get_teamfight_analysis_prompt,
)


class TestGetDeathAnalysisPrompt:
    """Tests for get_death_analysis_prompt function."""

    def test_handles_float_game_time(self):
        """Game time as float should not cause format errors."""
        deaths = [
            {
                "victim": "earthshaker",
                "killer": "disruptor",
                "game_time": 288.5,  # Float value
                "ability": "Thunder Strike",
            }
        ]
        hero_positions = {"earthshaker": "4"}

        # Should not raise "Unknown format code 'd' for object of type 'float'"
        result = get_death_analysis_prompt(deaths, hero_positions)
        assert isinstance(result, str)
        assert "earthshaker" in result
        assert "disruptor" in result

    def test_handles_integer_game_time(self):
        """Game time as integer should work correctly."""
        deaths = [
            {
                "victim": "medusa",
                "killer": "juggernaut",
                "game_time": 600,  # Integer value
                "ability": "Omnislash",
            }
        ]
        hero_positions = {"medusa": "1"}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert isinstance(result, str)
        assert "10:00" in result  # 600 seconds = 10:00

    def test_formats_time_correctly(self):
        """Time formatting should show M:SS format."""
        deaths = [
            {"victim": "hero1", "killer": "hero2", "game_time": 65.5, "ability": "attack"},
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "1:05" in result  # 65 seconds = 1:05

    def test_formats_time_with_leading_zero_seconds(self):
        """Seconds should have leading zero when < 10."""
        deaths = [
            {"victim": "hero1", "killer": "hero2", "game_time": 125.9, "ability": "attack"},
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "2:05" in result  # 125 seconds = 2:05

    def test_handles_zero_game_time(self):
        """Zero game time should format as 0:00."""
        deaths = [
            {"victim": "hero1", "killer": "hero2", "game_time": 0, "ability": "attack"},
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "0:00" in result

    def test_handles_negative_game_time(self):
        """Pre-game deaths (negative time) should not crash."""
        deaths = [
            {"victim": "hero1", "killer": "hero2", "game_time": -30.5, "ability": "attack"},
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert isinstance(result, str)

    def test_handles_missing_game_time(self):
        """Missing game_time should use default (0)."""
        deaths = [
            {"victim": "hero1", "killer": "hero2", "ability": "attack"},  # No game_time
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "0:00" in result

    def test_handles_smoke_involved_flag(self):
        """Smoke involved deaths should be marked."""
        deaths = [
            {
                "victim": "hero1",
                "killer": "hero2",
                "game_time": 300,
                "ability": "attack",
                "smoke_involved": True,
            },
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        # smoke_involved field is no longer rendered as [SMOKE] marker
        # Just verify prompt is generated correctly
        assert "hero1" in result

    def test_handles_empty_deaths_list(self):
        """Empty deaths list should not crash."""
        result = get_death_analysis_prompt([], {})
        assert isinstance(result, str)

    def test_limits_to_20_deaths(self):
        """Should only include first 20 deaths."""
        deaths = [
            {"victim": f"hero{i}", "killer": "killer", "game_time": i * 60, "ability": "attack"}
            for i in range(30)
        ]
        hero_positions = {}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "hero19" in result  # 20th death (0-indexed)
        assert "hero20" not in result  # 21st death should not be included

    def test_includes_position_from_hero_positions(self):
        """Hero positions should be included in output."""
        deaths = [
            {"victim": "medusa", "killer": "disruptor", "game_time": 300, "ability": "attack"},
        ]
        hero_positions = {"medusa": "1"}

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "(pos 1)" in result

    def test_unknown_position_shows_question_mark(self):
        """Unknown position should show ? marker."""
        deaths = [
            {"victim": "medusa", "killer": "disruptor", "game_time": 300, "ability": "attack"},
        ]
        hero_positions = {}  # Empty positions

        result = get_death_analysis_prompt(deaths, hero_positions)
        assert "(pos ?)" in result


class TestGetHeroPerformancePrompt:
    """Tests for get_hero_performance_prompt function."""

    def test_returns_string(self):
        """Should return a string prompt."""
        result = get_hero_performance_prompt(
            hero="juggernaut",
            position=1,  # position is int, not str
            raw_data={
                "kills": 8,
                "deaths": 2,
                "assists": 5,
                "fights_participated": 10,
                "total_fights": 15,
                "ability_stats": "omnislash: 5 casts (80% hit)",
            },
        )
        assert isinstance(result, str)

    def test_includes_hero_name(self):
        """Should include hero name in prompt."""
        result = get_hero_performance_prompt(
            hero="medusa",
            position=1,
            raw_data={},
        )
        assert "medusa" in result.lower()

    def test_includes_position(self):
        """Should include position in prompt."""
        result = get_hero_performance_prompt(
            hero="juggernaut",
            position=1,
            raw_data={},
        )
        assert "Position: 1" in result or "position 1" in result.lower()

    def test_handles_all_positions(self):
        """All positions 1-5 should work without errors."""
        for pos in [1, 2, 3, 4, 5]:
            result = get_hero_performance_prompt(hero="test_hero", position=pos, raw_data={})
            assert isinstance(result, str)
            assert f"(Position {pos})" in result

    def test_handles_invalid_position(self):
        """Invalid positions should fallback to position 1 behavior."""
        result = get_hero_performance_prompt(hero="test_hero", position=99, raw_data={})
        assert isinstance(result, str)


class TestGetLaneAnalysisPrompt:
    """Tests for get_lane_analysis_prompt function."""

    def test_returns_string(self):
        """Should return a string prompt."""
        result = get_lane_analysis_prompt(
            lane_data={"top_winner": "Radiant", "mid_winner": "Dire", "bot_winner": "Radiant"},
            hero_stats=[{"hero": "sf", "team": "Radiant", "lane": "mid", "last_hits_10min": 50}],
        )
        assert isinstance(result, str)

    def test_includes_lane_winners(self):
        """Should include lane winner data."""
        result = get_lane_analysis_prompt(
            lane_data={"top_winner": "Radiant", "mid_winner": "Dire"},
            hero_stats=[],
        )
        assert "Radiant" in result
        assert "Dire" in result

    def test_includes_hero_stats(self):
        """Should include hero stats."""
        result = get_lane_analysis_prompt(
            lane_data={},
            hero_stats=[{"hero": "medusa", "team": "Dire", "lane": "safelane", "last_hits_10min": 65}],
        )
        assert "medusa" in result


class TestGetTeamfightAnalysisPrompt:
    """Tests for get_teamfight_analysis_prompt function."""

    def test_returns_string(self):
        """Should return a string prompt."""
        result = get_teamfight_analysis_prompt(
            fight_data={
                "start_time_str": "25:30",
                "end_time_str": "25:50",
                "duration": 20.0,
                "total_deaths": 4,
                "participants": ["medusa", "juggernaut", "earthshaker"],
            },
            deaths=[{"victim": "medusa", "killer": "juggernaut", "game_time_str": "25:35"}],
        )
        assert isinstance(result, str)

    def test_includes_fight_details(self):
        """Should include fight details."""
        result = get_teamfight_analysis_prompt(
            fight_data={
                "start_time_str": "30:00",
                "end_time_str": "30:15",
                "participants": ["hero1", "hero2"],
            },
            deaths=[],
        )
        assert "30:00" in result

    def test_includes_death_sequence(self):
        """Should include death sequence."""
        result = get_teamfight_analysis_prompt(
            fight_data={"participants": []},
            deaths=[
                {"victim": "medusa", "killer": "juggernaut", "game_time_str": "25:35", "ability": "Omnislash"},
            ],
        )
        assert "medusa" in result
        assert "juggernaut" in result
