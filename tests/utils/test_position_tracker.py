"""Tests for position classification logic."""

import pytest

from src.utils.position_tracker import VALID_REGIONS, classify_map_position


class TestDireTriangleFix:
    """Tests for the Dire triangle location fix - the main bug we're preventing."""

    def test_top_left_is_not_dire_triangle(self):
        """Top-left quadrant (negative X, positive Y) should NOT be Dire triangle.

        This was the original bug - coordinates like (-4403, 4972) were incorrectly
        classified as 'dire_triangle' when they're actually on the opposite side of the map.
        """
        result = classify_map_position(-4403, 4972)
        assert result.region != "dire_triangle"

    def test_negative_x_never_dire_triangle(self):
        """Any negative X coordinate should never be Dire triangle."""
        test_coords = [
            (-5000, 5000),
            (-3000, 4000),
            (-4500, 3500),
            (-2000, 5500),
        ]
        for x, y in test_coords:
            result = classify_map_position(x, y)
            assert result.region != "dire_triangle", f"({x}, {y}) incorrectly classified as dire_triangle"

    def test_dire_triangle_requires_positive_x(self):
        """Dire triangle coordinates have positive X (right side of map)."""
        # These are valid dire_triangle coordinates
        result = classify_map_position(5100, 2800)
        assert result.region == "dire_triangle"

    def test_radiant_triangle_has_positive_x_negative_y(self):
        """Radiant triangle is bottom-right: positive X, negative Y."""
        result = classify_map_position(4000, -4000)
        assert result.region == "radiant_triangle"


class TestKeyLandmarks:
    """Test key map landmarks with well-defined boundaries."""

    def test_roshan_pit(self):
        """Roshan pit near top power rune."""
        result = classify_map_position(-2000, 1200)
        assert result.region == "roshan_pit"

    def test_tormentor_radiant(self):
        """Radiant tormentor location."""
        result = classify_map_position(-4100, -400)
        assert result.region == "tormentor_radiant"

    def test_tormentor_dire(self):
        """Dire tormentor location."""
        result = classify_map_position(4100, 0)
        assert result.region == "tormentor_dire"

    def test_radiant_base_deep(self):
        """Deep in Radiant base, away from T4 towers."""
        result = classify_map_position(-7000, -6500)
        assert result.region == "radiant_base"

    def test_dire_base_deep(self):
        """Deep in Dire base, away from T4 towers."""
        result = classify_map_position(7000, 6500)
        assert result.region == "dire_base"


class TestTowerPriority:
    """Test that tower proximity takes priority over area classification."""

    def test_near_tower_returns_tower_region(self):
        """Coordinates within 1200 units of a tower return tower region."""
        # Near Dire T1 mid (at approximately 524, 652)
        result = classify_map_position(500, 700)
        assert result.region == "dire_t1_mid"
        assert result.tower_distance < 1200

    def test_far_from_tower_returns_area_region(self):
        """Coordinates far from towers return area-based region."""
        result = classify_map_position(5100, 2800)
        assert result.tower_distance > 1200
        assert result.region == "dire_triangle"


class TestMapPositionFields:
    """Test that MapPosition has all expected fields."""

    def test_has_coordinates(self):
        """MapPosition includes original coordinates."""
        result = classify_map_position(1000, 2000)
        assert result.x == 1000
        assert result.y == 2000

    def test_has_region(self):
        """MapPosition includes region classification."""
        result = classify_map_position(1000, 2000)
        assert result.region is not None
        assert isinstance(result.region, str)

    def test_has_location_string(self):
        """MapPosition includes human-readable location."""
        result = classify_map_position(1000, 2000)
        assert result.location is not None
        assert isinstance(result.location, str)

    def test_has_tower_info(self):
        """MapPosition includes tower distance."""
        result = classify_map_position(500, 700)
        assert result.tower_distance is not None
        assert isinstance(result.tower_distance, int)


class TestValidRegions:
    """Test that classified regions are always valid."""

    @pytest.mark.parametrize("x,y", [
        (-7000, -6500),  # radiant base
        (7000, 6500),  # dire base
        (4000, -4000),  # radiant triangle
        (5100, 2800),  # dire triangle
        (-2000, 1200),  # roshan
        (-4100, -400),  # radiant tormentor
        (4100, 0),  # dire tormentor
        (500, 700),  # near tower
        (0, 0),  # center
        (-5000, 5000),  # top area
        (5000, -5000),  # bot area
    ])
    def test_all_regions_are_valid(self, x, y):
        """All classified regions should be in VALID_REGIONS list."""
        result = classify_map_position(x, y)
        assert result.region in VALID_REGIONS, f"Region '{result.region}' at ({x}, {y}) not in VALID_REGIONS"
