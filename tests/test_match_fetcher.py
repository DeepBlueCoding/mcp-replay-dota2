"""Tests for match_fetcher module."""

import pytest

from src.utils.match_fetcher import get_lane_name

# Mark all tests in this module as fast (no replay parsing needed)
pytestmark = pytest.mark.fast


class TestGetLaneName:
    """Tests for get_lane_name function."""

    def test_mid_lane_radiant(self):
        assert get_lane_name(2, is_radiant=True) == "mid_lane"

    def test_mid_lane_dire(self):
        assert get_lane_name(2, is_radiant=False) == "mid_lane"

    def test_jungle_radiant(self):
        assert get_lane_name(4, is_radiant=True) == "jungle"

    def test_jungle_dire(self):
        assert get_lane_name(4, is_radiant=False) == "jungle"

    def test_radiant_bottom_is_safe_lane(self):
        """Bottom lane (1) is Radiant's safe lane."""
        assert get_lane_name(1, is_radiant=True) == "safe_lane"

    def test_radiant_top_is_off_lane(self):
        """Top lane (3) is Radiant's off lane."""
        assert get_lane_name(3, is_radiant=True) == "off_lane"

    def test_dire_top_is_safe_lane(self):
        """Top lane (3) is Dire's safe lane."""
        assert get_lane_name(3, is_radiant=False) == "safe_lane"

    def test_dire_bottom_is_off_lane(self):
        """Bottom lane (1) is Dire's off lane."""
        assert get_lane_name(1, is_radiant=False) == "off_lane"

    def test_unknown_lane_returns_none(self):
        assert get_lane_name(0, is_radiant=True) is None
        assert get_lane_name(5, is_radiant=False) is None
        assert get_lane_name(99, is_radiant=True) is None
