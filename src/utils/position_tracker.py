"""
Position classification for Dota 2 map coordinates.

Provides PositionClassifier class and legacy function to classify world coordinates
into human-readable map locations (lanes, regions, nearby landmarks).
"""

import logging
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Tuple

if TYPE_CHECKING:
    from src.models.map_data import MapData

logger = logging.getLogger(__name__)


@dataclass
class MapPosition:
    """A position on the Dota 2 map with classification."""

    x: float
    y: float
    region: str
    lane: Optional[str]
    location: str
    closest_tower: Optional[str]
    tower_distance: int


class PositionClassifier:
    """
    Version-aware position classifier using MapData.

    Extracts tower positions, landmarks, and lane boundaries from MapData
    and uses them for position classification.
    """

    def __init__(self, map_data: "MapData"):
        """
        Initialize classifier with versioned map data.

        Args:
            map_data: MapData instance with towers, landmarks, lane_boundaries
        """
        self._towers: Dict[str, Tuple[float, float]] = {}
        for tower in map_data.towers:
            self._towers[tower.name] = (tower.position.x, tower.position.y)

        self._landmarks: Dict[str, Tuple[float, float]] = {}
        for landmark in map_data.landmarks:
            self._landmarks[landmark.name] = (landmark.position.x, landmark.position.y)

        self._lane_boundaries: Dict[str, Dict[str, float]] = {}
        for boundary in map_data.lane_boundaries:
            self._lane_boundaries[boundary.name] = {
                "x_min": boundary.x_min,
                "x_max": boundary.x_max,
                "y_min": boundary.y_min,
                "y_max": boundary.y_max,
            }

        self._ancients: Dict[str, Tuple[float, float]] = {}
        for ancient in map_data.ancients:
            self._ancients[ancient.team] = (ancient.position.x, ancient.position.y)

    def classify(self, x: float, y: float) -> MapPosition:
        """
        Classify a map position into a human-readable location.

        Args:
            x: World X coordinate
            y: World Y coordinate

        Returns:
            MapPosition with region, lane, and nearby landmark info
        """
        closest_tower, min_tower_dist = self._find_closest_tower(x, y)
        lane = self._classify_lane(x, y)
        region = self._classify_region(x, y, lane)
        location = self._build_location_string(region, closest_tower, min_tower_dist)

        return MapPosition(
            x=x,
            y=y,
            region=region,
            lane=lane,
            location=location,
            closest_tower=closest_tower if min_tower_dist < 1200 else None,
            tower_distance=int(min_tower_dist),
        )

    def _find_closest_tower(self, x: float, y: float) -> Tuple[Optional[str], float]:
        """Find the closest tower to the position."""
        closest_tower = None
        min_dist = float("inf")
        for name, pos in self._towers.items():
            d = self._distance((x, y), pos)
            if d < min_dist:
                min_dist = d
                closest_tower = name
        return closest_tower, min_dist

    def _classify_lane(self, x: float, y: float) -> Optional[str]:
        """Classify position into a lane using lane boundaries."""
        if self._lane_boundaries:
            for lane_name, bounds in self._lane_boundaries.items():
                if (
                    bounds["x_min"] <= x <= bounds["x_max"]
                    and bounds["y_min"] <= y <= bounds["y_max"]
                ):
                    return lane_name
            return None

        # Fallback to legacy hardcoded logic if no boundaries defined
        if y > 3500 or (x < -3500 and y > 1500):
            return "top"
        elif y < -3500 or (x > 3500 and y < -1500):
            return "bot"
        elif -2500 < x < 2500 and -2500 < y < 2500:
            return "mid"
        return None

    def _classify_region(self, x: float, y: float, lane: Optional[str]) -> str:
        """Classify position into a map region."""
        on_dire_side = y > x * 0.8 - 500

        if x < -5000 and y < -4500:
            return "radiant_base"
        elif x > 5000 and y > 4000:
            return "dire_base"
        elif lane == "mid" or (-2000 < x < 2000 and -2000 < y < 2000):
            return "river" if -1500 < y - x * 0.8 < 1500 else "mid_lane"
        elif lane == "top":
            return "dire_safelane" if on_dire_side else "radiant_offlane"
        elif lane == "bot":
            return "dire_offlane" if on_dire_side else "radiant_safelane"
        elif on_dire_side:
            return "dire_jungle"
        else:
            return "radiant_jungle"

    def _build_location_string(
        self, region: str, closest_tower: Optional[str], tower_dist: float
    ) -> str:
        """Build a human-readable location string."""
        if tower_dist < 1200 and closest_tower:
            parts = closest_tower.split("_")
            team = parts[0].capitalize()
            tier = parts[1].upper()
            lane_name = parts[2] if len(parts) > 2 else ""
            return f"{region.replace('_', ' ')}, near {team} {tier} {lane_name}"
        return region.replace("_", " ")

    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate distance between two points."""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# Legacy hardcoded data for backwards compatibility
_LEGACY_TOWER_POSITIONS = {
    "radiant_t1_top": (-6336, 1856),
    "radiant_t1_mid": (-360, -6256),
    "radiant_t1_bot": (4904, -6198),
    "radiant_t2_top": (-6464, -872),
    "radiant_t2_mid": (-4640, -4144),
    "radiant_t2_bot": (-3190, -2926),
    "radiant_t3_top": (-6592, -3408),
    "radiant_t3_mid": (-4096, -448),
    "radiant_t3_bot": (-3952, -6112),
    "dire_t1_top": (-5275, 5928),
    "dire_t1_mid": (524, 652),
    "dire_t1_bot": (6269, -2240),
    "dire_t2_top": (-128, 6016),
    "dire_t2_mid": (2496, 2112),
    "dire_t2_bot": (6400, 384),
    "dire_t3_top": (3552, 5776),
    "dire_t3_mid": (3392, -448),
    "dire_t3_bot": (6336, 3032),
}

# Singleton classifier for legacy function
_default_classifier: Optional[PositionClassifier] = None


def _get_default_classifier() -> PositionClassifier:
    """Get or create the default classifier using 7.39 map data."""
    global _default_classifier
    if _default_classifier is None:
        from src.resources.versioned_map_resources import get_versioned_map_data

        provider = get_versioned_map_data()
        map_data = provider.get_map_data("7.39")
        _default_classifier = PositionClassifier(map_data)
    return _default_classifier


def classify_map_position(x: float, y: float) -> MapPosition:
    """
    Classify a map position into a human-readable location.

    This is a backwards-compatible function that uses 7.39 map data.
    For version-aware classification, use PositionClassifier directly.

    Args:
        x: World X coordinate
        y: World Y coordinate

    Returns:
        MapPosition with region, lane, and nearby landmark info
    """
    return _get_default_classifier().classify(x, y)
