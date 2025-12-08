"""
Tests for timeline parsing and response models.

Tests the TimelineParser and Pydantic models for timeline data.
"""

import pytest

from src.models.tool_responses import (
    KDASnapshot,
    MatchTimelineResponse,
    PlayerStatsAtMinute,
    PlayerTimeline,
    StatsAtMinuteResponse,
    TeamGraphs,
)
from src.utils.timeline_parser import TimelineParser


class TestTimelineModels:
    """Tests for Pydantic timeline models."""

    def test_kda_snapshot_creation(self):
        """Test KDASnapshot model with all fields."""
        snap = KDASnapshot(
            game_time=600.0,
            kills=5,
            deaths=2,
            assists=10,
            level=12,
        )
        assert snap.game_time == 600.0
        assert snap.kills == 5
        assert snap.deaths == 2
        assert snap.assists == 10
        assert snap.level == 12

    def test_player_timeline_creation(self):
        """Test PlayerTimeline model with timeline data."""
        timeline = PlayerTimeline(
            hero="antimage",
            team="radiant",
            net_worth=[0, 500, 1200, 2500, 4000],
            hero_damage=[0, 100, 300, 800, 1500],
            kda_timeline=[
                KDASnapshot(game_time=0, kills=0, deaths=0, assists=0, level=1),
                KDASnapshot(game_time=300, kills=1, deaths=0, assists=0, level=6),
                KDASnapshot(game_time=600, kills=3, deaths=1, assists=2, level=11),
            ],
        )
        assert timeline.hero == "antimage"
        assert timeline.team == "radiant"
        assert len(timeline.net_worth) == 5
        assert len(timeline.kda_timeline) == 3
        assert timeline.kda_timeline[2].kills == 3

    def test_team_graphs_creation(self):
        """Test TeamGraphs model."""
        graphs = TeamGraphs(
            radiant_xp=[0, 1000, 5000, 12000],
            dire_xp=[0, 900, 4800, 11500],
            radiant_gold=[0, 800, 4000, 10000],
            dire_gold=[0, 750, 3800, 9500],
        )
        assert len(graphs.radiant_xp) == 4
        assert graphs.radiant_xp[3] == 12000
        assert graphs.dire_gold[2] == 3800

    def test_match_timeline_response_success(self):
        """Test successful timeline response."""
        response = MatchTimelineResponse(
            success=True,
            match_id=8461956309,
            players=[
                PlayerTimeline(
                    hero="medusa",
                    team="radiant",
                    net_worth=[0, 500],
                    hero_damage=[0, 100],
                    kda_timeline=[],
                ),
            ],
            team_graphs=TeamGraphs(
                radiant_xp=[0, 1000],
                dire_xp=[0, 900],
                radiant_gold=[0, 800],
                dire_gold=[0, 750],
            ),
        )
        assert response.success is True
        assert response.match_id == 8461956309
        assert len(response.players) == 1
        assert response.team_graphs is not None

    def test_match_timeline_response_error(self):
        """Test timeline response with error."""
        response = MatchTimelineResponse(
            success=False,
            error="No metadata found in replay",
        )
        assert response.success is False
        assert response.error == "No metadata found in replay"
        assert response.players == []
        assert response.team_graphs is None

    def test_player_stats_at_minute(self):
        """Test PlayerStatsAtMinute model."""
        stats = PlayerStatsAtMinute(
            hero="earthshaker",
            team="dire",
            net_worth=4500,
            hero_damage=3200,
            kills=2,
            deaths=1,
            assists=8,
            level=10,
        )
        assert stats.hero == "earthshaker"
        assert stats.team == "dire"
        assert stats.net_worth == 4500
        assert stats.kills == 2
        assert stats.level == 10

    def test_stats_at_minute_response(self):
        """Test StatsAtMinuteResponse model."""
        response = StatsAtMinuteResponse(
            success=True,
            match_id=8461956309,
            minute=10,
            players=[
                PlayerStatsAtMinute(
                    hero="medusa",
                    team="radiant",
                    net_worth=5000,
                    hero_damage=2000,
                    kills=1,
                    deaths=0,
                    assists=2,
                    level=11,
                ),
            ],
        )
        assert response.success is True
        assert response.minute == 10
        assert len(response.players) == 1


class TestTimelineParserUnit:
    """Unit tests for TimelineParser without real replay data."""

    def test_parser_instantiation(self):
        """Test TimelineParser can be instantiated."""
        parser = TimelineParser()
        assert parser is not None

    def test_parse_timeline_no_metadata(self):
        """Test parse_timeline returns None when no metadata."""
        from unittest.mock import MagicMock

        parser = TimelineParser()
        mock_data = MagicMock()
        mock_data.metadata = None

        result = parser.parse_timeline(mock_data)
        assert result is None

    def test_parse_timeline_empty_teams(self):
        """Test parse_timeline returns None when not enough teams."""
        from unittest.mock import MagicMock

        parser = TimelineParser()
        mock_data = MagicMock()
        mock_data.metadata = {"metadata": {"teams": []}}

        result = parser.parse_timeline(mock_data)
        assert result is None

    def test_get_stats_at_minute_empty(self):
        """Test get_stats_at_minute with empty timeline."""
        parser = TimelineParser()
        timeline = {"players": []}

        result = parser.get_stats_at_minute(timeline, 10)
        assert result["minute"] == 10
        assert result["players"] == []


class TestTimelineParserIntegration:
    """Integration tests using real replay data."""

    @pytest.fixture
    def parsed_data(self, parsed_replay_data):
        """Get parsed replay data from conftest fixture."""
        return parsed_replay_data

    def test_parse_timeline_with_real_data(self, parsed_data):
        """Test timeline parsing with real replay data."""
        parser = TimelineParser()
        timeline = parser.parse_timeline(parsed_data)

        # If metadata is available, timeline should work
        if parsed_data.metadata is not None:
            assert timeline is not None
            assert "players" in timeline
            assert "radiant" in timeline
            assert "dire" in timeline
            # Should have 10 players (5 per team)
            assert len(timeline["players"]) == 10
        else:
            # If no metadata, parsing returns None
            assert timeline is None

    def test_get_stats_at_10_minutes(self, parsed_data):
        """Test getting stats at 10 minute mark."""
        parser = TimelineParser()
        timeline = parser.parse_timeline(parsed_data)

        if timeline is not None:
            stats = parser.get_stats_at_minute(timeline, 10)
            assert stats["minute"] == 10
            # Should have stats for all 10 players
            assert len(stats["players"]) == 10
            # Each player should have team info
            for player in stats["players"]:
                assert "team" in player
                assert player["team"] in ["radiant", "dire"]

    def test_timeline_has_net_worth_progression(self, parsed_data):
        """Test that timeline contains net worth progression data."""
        parser = TimelineParser()
        timeline = parser.parse_timeline(parsed_data)

        if timeline is not None:
            for player in timeline["players"]:
                nw = player.get("net_worth", [])
                # Net worth should generally increase over time
                if len(nw) >= 2:
                    # Early game net worth should be less than late game
                    assert nw[-1] >= nw[0], "Net worth should grow over time"

    def test_team_graphs_have_data(self, parsed_data):
        """Test that team graphs contain XP and gold data."""
        parser = TimelineParser()
        timeline = parser.parse_timeline(parsed_data)

        if timeline is not None:
            radiant = timeline.get("radiant", {})
            dire = timeline.get("dire", {})

            # Teams should have graph data
            assert "graph_experience" in radiant or "graph_gold_earned" in radiant
            assert "graph_experience" in dire or "graph_gold_earned" in dire
