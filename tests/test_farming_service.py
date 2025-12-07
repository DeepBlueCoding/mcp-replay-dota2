"""
Tests for the FarmingService.

Tests creep classification, camp pattern matching, time formatting,
and farming data models.
These are pure unit tests that don't require replay data.
"""

import pytest

from src.services.farming.farming_service import (
    CAMP_TIERS,
    NEUTRAL_CAMP_PATTERNS,
    FarmingService,
)
from src.services.models.farming_data import (
    CampClear,
    CreepKill,
    ItemTiming,
    LevelTiming,
    MapPositionSnapshot,
    MinuteFarmingData,
    MultiCampClear,
)

# Mark all tests in this module as fast (no replay parsing needed)
pytestmark = pytest.mark.fast


class TestCreepClassification:
    """Tests for creep type classification."""

    @pytest.fixture
    def service(self):
        return FarmingService()

    def test_classify_lane_creep_goodguys(self, service):
        """Lane creeps from goodguys (Radiant) are classified as lane."""
        creep_type, camp = service._classify_creep("npc_dota_creep_goodguys_melee")
        assert creep_type == "lane"
        assert camp is None

    def test_classify_lane_creep_badguys(self, service):
        """Lane creeps from badguys (Dire) are classified as lane."""
        creep_type, camp = service._classify_creep("npc_dota_creep_badguys_ranged")
        assert creep_type == "lane"
        assert camp is None

    def test_classify_neutral_satyr(self, service):
        """Satyr neutrals are classified correctly."""
        creep_type, camp = service._classify_creep("npc_dota_neutral_satyr_hellcaller")
        assert creep_type == "neutral"
        assert camp == "large_satyr"

    def test_classify_neutral_centaur(self, service):
        """Centaur neutrals are classified correctly."""
        creep_type, camp = service._classify_creep("npc_dota_neutral_centaur_khan")
        assert creep_type == "neutral"
        assert camp == "large_centaur"

    def test_classify_neutral_kobold(self, service):
        """Kobold neutrals are classified correctly."""
        creep_type, camp = service._classify_creep("npc_dota_neutral_kobold_taskmaster")
        assert creep_type == "neutral"
        assert camp == "small_kobold"

    def test_classify_neutral_ancient(self, service):
        """Ancient neutrals are classified correctly."""
        creep_type, camp = service._classify_creep("npc_dota_neutral_black_dragon")
        assert creep_type == "neutral"
        assert camp == "ancient_black_dragon"

    def test_classify_neutral_unknown(self, service):
        """Unknown neutrals are classified as neutral with unknown camp."""
        creep_type, camp = service._classify_creep("npc_dota_neutral_some_new_creep")
        assert creep_type == "neutral"
        assert camp == "unknown"

    def test_classify_other_ward(self, service):
        """Wards are classified as other."""
        creep_type, camp = service._classify_creep("npc_dota_observer_wards")
        assert creep_type == "other"
        assert camp is None

    def test_classify_other_summon(self, service):
        """Summons are classified as other."""
        creep_type, camp = service._classify_creep("npc_dota_lone_druid_bear")
        assert creep_type == "other"
        assert camp is None

    def test_classify_empty_name(self, service):
        """Empty names are classified as other."""
        creep_type, camp = service._classify_creep("")
        assert creep_type == "other"
        assert camp is None

    def test_classify_none_name(self, service):
        """None names are classified as other."""
        creep_type, camp = service._classify_creep(None)
        assert creep_type == "other"
        assert camp is None


class TestCampTiers:
    """Tests for camp tier classification."""

    @pytest.fixture
    def service(self):
        return FarmingService()

    def test_ancient_tier(self, service):
        """Ancient camps are tier 'ancient'."""
        assert service._get_camp_tier("ancient_black_dragon") == "ancient"
        assert service._get_camp_tier("ancient_granite") == "ancient"

    def test_large_tier(self, service):
        """Large camps are tier 'large'."""
        assert service._get_camp_tier("large_satyr") == "large"
        assert service._get_camp_tier("large_centaur") == "large"

    def test_medium_tier(self, service):
        """Medium camps are tier 'medium'."""
        assert service._get_camp_tier("medium_wolf") == "medium"
        assert service._get_camp_tier("medium_harpy") == "medium"

    def test_small_tier(self, service):
        """Small camps are tier 'small'."""
        assert service._get_camp_tier("small_kobold") == "small"
        assert service._get_camp_tier("small_ghost") == "small"

    def test_unknown_tier(self, service):
        """Unknown camps return None tier."""
        assert service._get_camp_tier("unknown") is None
        assert service._get_camp_tier(None) is None


class TestTimeFormatting:
    """Tests for time formatting."""

    @pytest.fixture
    def service(self):
        return FarmingService()

    def test_format_zero(self, service):
        """Zero seconds formats as 0:00."""
        assert service._format_time(0) == "0:00"

    def test_format_one_minute(self, service):
        """60 seconds formats as 1:00."""
        assert service._format_time(60) == "1:00"

    def test_format_mixed(self, service):
        """Mixed time formats correctly."""
        assert service._format_time(338) == "5:38"
        assert service._format_time(396) == "6:36"
        assert service._format_time(599) == "9:59"


class TestHeroNameCleaning:
    """Tests for hero name cleaning."""

    @pytest.fixture
    def service(self):
        return FarmingService()

    def test_clean_full_name(self, service):
        """Full hero names are cleaned correctly."""
        assert service._clean_hero_name("npc_dota_hero_terrorblade") == "terrorblade"
        assert service._clean_hero_name("npc_dota_hero_antimage") == "antimage"

    def test_clean_short_name(self, service):
        """Short names without prefix are returned as-is."""
        assert service._clean_hero_name("terrorblade") == "terrorblade"

    def test_clean_empty(self, service):
        """Empty names return empty string."""
        assert service._clean_hero_name("") == ""
        assert service._clean_hero_name(None) == ""


class TestNeutralPatternCoverage:
    """Tests to verify neutral camp pattern coverage."""

    def test_all_patterns_have_tiers(self):
        """All neutral patterns should have a tier classification."""
        all_tier_camps = set()
        for camps in CAMP_TIERS.values():
            all_tier_camps.update(camps)

        for camp_type in set(NEUTRAL_CAMP_PATTERNS.values()):
            assert camp_type in all_tier_camps, f"{camp_type} not in any tier"

    def test_common_neutrals_covered(self):
        """Common neutral creep names are in the pattern list."""
        common_neutrals = [
            "satyr_hellcaller",
            "centaur_khan",
            "dark_troll_warlord",
            "hellbear_smasher",
            "wildwing_ripper",
            "alpha_wolf",
            "harpy_stormcrafter",
            "kobold_taskmaster",
            "gnoll_assassin",
            "black_dragon",
            "granite_golem",
        ]
        for neutral in common_neutrals:
            assert any(
                neutral in pattern for pattern in NEUTRAL_CAMP_PATTERNS
            ), f"{neutral} not covered by patterns"


class TestFarmingDataModels:
    """Tests for farming data model structures."""

    def test_camp_clear_model(self):
        """CampClear model stores camp clear data correctly."""
        camp = CampClear(
            time_str="14:05",
            camp="large_troll",
            tier="large",
            area="dire_jungle",
        )
        assert camp.time_str == "14:05"
        assert camp.camp == "large_troll"
        assert camp.tier == "large"
        assert camp.area == "dire_jungle"

    def test_map_position_snapshot_model(self):
        """MapPositionSnapshot model stores position data correctly."""
        pos = MapPositionSnapshot(
            x=5200.5,
            y=3800.3,
            area="dire_jungle",
        )
        assert pos.x == 5200.5
        assert pos.y == 3800.3
        assert pos.area == "dire_jungle"

    def test_level_timing_model(self):
        """LevelTiming model stores level timing data correctly."""
        timing = LevelTiming(
            level=6,
            time=420.0,
            time_str="7:00",
        )
        assert timing.level == 6
        assert timing.time == 420.0
        assert timing.time_str == "7:00"

    def test_item_timing_model(self):
        """ItemTiming model stores item purchase data correctly."""
        timing = ItemTiming(
            item="bfury",
            time=840.0,
            time_str="14:00",
        )
        assert timing.item == "bfury"
        assert timing.time == 840.0
        assert timing.time_str == "14:00"

    def test_creep_kill_with_position(self):
        """CreepKill model includes position data."""
        kill = CreepKill(
            game_time=517.3,
            game_time_str="8:37",
            creep_name="npc_dota_neutral_dark_troll_warlord",
            creep_type="neutral",
            neutral_camp="large_troll",
            position_x=5100.0,
            position_y=3900.0,
            map_area="dire_jungle",
        )
        assert kill.game_time == 517.3
        assert kill.neutral_camp == "large_troll"
        assert kill.map_area == "dire_jungle"
        assert kill.position_x == 5100.0

    def test_minute_farming_data_with_camp_sequence(self):
        """MinuteFarmingData model includes camp sequence and positions."""
        camp1 = CampClear(time_str="14:05", camp="large_troll", tier="large", area="dire_jungle")
        camp2 = CampClear(time_str="14:18", camp="medium_satyr", tier="medium", area="dire_jungle")

        pos_start = MapPositionSnapshot(x=5200.0, y=3800.0, area="dire_jungle")
        pos_end = MapPositionSnapshot(x=5400.0, y=4200.0, area="dire_jungle")

        minute_data = MinuteFarmingData(
            minute=14,
            position_at_start=pos_start,
            position_at_end=pos_end,
            camp_sequence=[camp1, camp2],
            lane_creeps_killed=3,
            camps_cleared=2,
            gold=8500,
            last_hits=142,
            level=12,
        )

        assert minute_data.minute == 14
        assert minute_data.position_at_start.area == "dire_jungle"
        assert minute_data.position_at_end.x == 5400.0
        assert len(minute_data.camp_sequence) == 2
        assert minute_data.camp_sequence[0].camp == "large_troll"
        assert minute_data.camp_sequence[1].camp == "medium_satyr"
        assert minute_data.camps_cleared == 2
        assert minute_data.lane_creeps_killed == 3

    def test_minute_farming_data_empty_sequence(self):
        """MinuteFarmingData works with empty camp sequence (lane-only minute)."""
        minute_data = MinuteFarmingData(
            minute=3,
            lane_creeps_killed=8,
            camps_cleared=0,
            gold=1200,
            last_hits=24,
            level=4,
        )

        assert minute_data.minute == 3
        assert minute_data.camp_sequence == []
        assert minute_data.camps_cleared == 0
        assert minute_data.lane_creeps_killed == 8
        assert minute_data.position_at_start is None
        assert minute_data.position_at_end is None


class TestMultiCampDetection:
    """Tests for multi-camp clear detection (stacked/adjacent farming)."""

    @pytest.fixture
    def service(self):
        return FarmingService()

    def test_multi_camp_clear_model(self):
        """MultiCampClear model stores multi-camp data correctly."""
        multi = MultiCampClear(
            time_str="14:05",
            camps=["large_centaur", "medium_wolf"],
            duration_seconds=2.1,
            creeps_killed=5,
            area="dire_jungle",
        )
        assert multi.time_str == "14:05"
        assert multi.camps == ["large_centaur", "medium_wolf"]
        assert multi.duration_seconds == 2.1
        assert multi.creeps_killed == 5
        assert multi.area == "dire_jungle"

    def test_detect_multi_camp_two_camps_within_window(self, service):
        """Detects when two different camps are killed within time window."""
        kills = [
            CreepKill(game_time=845.3, game_time_str="14:05", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
            CreepKill(game_time=845.9, game_time_str="14:05", creep_name="alpha_wolf",
                      creep_type="neutral", neutral_camp="medium_wolf", map_area="dire_jungle"),
            CreepKill(game_time=846.1, game_time_str="14:06", creep_name="centaur_outrunner",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
            CreepKill(game_time=846.4, game_time_str="14:06", creep_name="giant_wolf",
                      creep_type="neutral", neutral_camp="medium_wolf", map_area="dire_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 1
        assert set(result[0].camps) == {"large_centaur", "medium_wolf"}
        assert result[0].creeps_killed == 4
        assert result[0].duration_seconds == 1.1  # 846.4 - 845.3

    def test_detect_multi_camp_no_detection_single_camp(self, service):
        """Does not detect multi-camp when only one camp type is killed."""
        kills = [
            CreepKill(game_time=845.0, game_time_str="14:05", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
            CreepKill(game_time=845.5, game_time_str="14:05", creep_name="centaur_outrunner",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 0

    def test_detect_multi_camp_no_detection_outside_window(self, service):
        """Does not detect multi-camp when kills are too far apart."""
        kills = [
            CreepKill(game_time=845.0, game_time_str="14:05", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
            CreepKill(game_time=850.0, game_time_str="14:10", creep_name="alpha_wolf",
                      creep_type="neutral", neutral_camp="medium_wolf", map_area="dire_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 0

    def test_detect_multi_camp_ignores_lane_creeps(self, service):
        """Lane creeps are not included in multi-camp detection."""
        kills = [
            CreepKill(game_time=845.0, game_time_str="14:05", creep_name="lane_creep",
                      creep_type="lane", neutral_camp=None, map_area="dire_jungle"),
            CreepKill(game_time=845.5, game_time_str="14:05", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 0

    def test_detect_multi_camp_three_camps_stacked(self, service):
        """Detects when three camps are cleared together (triple stack)."""
        kills = [
            CreepKill(game_time=900.0, game_time_str="15:00", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
            CreepKill(game_time=900.5, game_time_str="15:00", creep_name="alpha_wolf",
                      creep_type="neutral", neutral_camp="medium_wolf", map_area="dire_jungle"),
            CreepKill(game_time=901.0, game_time_str="15:01", creep_name="satyr_hellcaller",
                      creep_type="neutral", neutral_camp="large_satyr", map_area="dire_jungle"),
            CreepKill(game_time=901.5, game_time_str="15:01", creep_name="centaur_outrunner",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 1
        assert len(result[0].camps) == 3
        assert set(result[0].camps) == {"large_centaur", "medium_wolf", "large_satyr"}

    def test_detect_multi_camp_multiple_events(self, service):
        """Detects multiple separate multi-camp clear events."""
        kills = [
            # First multi-camp at 14:00
            CreepKill(game_time=840.0, game_time_str="14:00", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
            CreepKill(game_time=840.5, game_time_str="14:00", creep_name="alpha_wolf",
                      creep_type="neutral", neutral_camp="medium_wolf", map_area="dire_jungle"),
            # Gap - single camp at 14:10
            CreepKill(game_time=850.0, game_time_str="14:10", creep_name="kobold",
                      creep_type="neutral", neutral_camp="small_kobold", map_area="radiant_jungle"),
            # Second multi-camp at 15:00
            CreepKill(game_time=900.0, game_time_str="15:00", creep_name="satyr_hellcaller",
                      creep_type="neutral", neutral_camp="large_satyr", map_area="radiant_jungle"),
            CreepKill(game_time=901.0, game_time_str="15:01", creep_name="hellbear_smasher",
                      creep_type="neutral", neutral_camp="large_hellbear", map_area="radiant_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 2
        assert set(result[0].camps) == {"large_centaur", "medium_wolf"}
        assert set(result[1].camps) == {"large_satyr", "large_hellbear"}

    def test_detect_multi_camp_empty_list(self, service):
        """Handles empty kill list gracefully."""
        result = service._detect_multi_camp_clears([])
        assert len(result) == 0

    def test_detect_multi_camp_single_kill(self, service):
        """Handles single kill gracefully."""
        kills = [
            CreepKill(game_time=845.0, game_time_str="14:05", creep_name="centaur_khan",
                      creep_type="neutral", neutral_camp="large_centaur", map_area="dire_jungle"),
        ]
        result = service._detect_multi_camp_clears(kills)
        assert len(result) == 0
