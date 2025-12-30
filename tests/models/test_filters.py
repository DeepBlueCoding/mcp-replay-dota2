"""Tests for filter models."""

import pytest

from src.models.combat_log import AbilityUsage, FightParticipation
from src.models.filters import (
    HeroPerformanceFilters,
    TimeRange,
)


class TestTimeRange:
    """Tests for TimeRange filter."""

    def test_contains_no_bounds(self):
        """TimeRange with no bounds contains all times."""
        tr = TimeRange()
        assert tr.contains(0)
        assert tr.contains(1000)
        assert tr.contains(-100)

    def test_contains_start_only(self):
        """TimeRange with start bound only."""
        tr = TimeRange(start=300)
        assert not tr.contains(299)
        assert tr.contains(300)
        assert tr.contains(1000)

    def test_contains_end_only(self):
        """TimeRange with end bound only."""
        tr = TimeRange(end=900)
        assert tr.contains(0)
        assert tr.contains(900)
        assert not tr.contains(901)

    def test_contains_both_bounds(self):
        """TimeRange with both bounds."""
        tr = TimeRange(start=300, end=900)
        assert not tr.contains(299)
        assert tr.contains(300)
        assert tr.contains(600)
        assert tr.contains(900)
        assert not tr.contains(901)


class TestHeroPerformanceFilters:
    """Tests for HeroPerformanceFilters."""

    @pytest.fixture
    def sample_fights(self) -> list[FightParticipation]:
        """Create sample fight participation data."""
        return [
            FightParticipation(
                fight_id="fight_1",
                fight_start=100.0,
                fight_start_str="1:40",
                fight_end=110.0,
                fight_end_str="1:50",
                is_teamfight=False,
                kills=1,
                deaths=0,
                assists=0,
                abilities_used=[
                    AbilityUsage(
                        ability="spirit_breaker_charge_of_darkness",
                        total_casts=1,
                        hero_hits=1,
                        hit_rate=100.0,
                    )
                ],
            ),
            FightParticipation(
                fight_id="fight_2",
                fight_start=500.0,
                fight_start_str="8:20",
                fight_end=520.0,
                fight_end_str="8:40",
                is_teamfight=True,
                kills=2,
                deaths=1,
                assists=1,
                abilities_used=[
                    AbilityUsage(
                        ability="spirit_breaker_charge_of_darkness",
                        total_casts=2,
                        hero_hits=3,
                        hit_rate=150.0,
                    ),
                    AbilityUsage(
                        ability="spirit_breaker_nether_strike",
                        total_casts=1,
                        hero_hits=1,
                        hit_rate=100.0,
                    ),
                ],
            ),
            FightParticipation(
                fight_id="fight_3",
                fight_start=1200.0,
                fight_start_str="20:00",
                fight_end=1230.0,
                fight_end_str="20:30",
                is_teamfight=True,
                kills=0,
                deaths=1,
                assists=2,
                abilities_used=[
                    AbilityUsage(
                        ability="spirit_breaker_charge_of_darkness",
                        total_casts=1,
                        hero_hits=2,
                        hit_rate=200.0,
                    ),
                ],
            ),
        ]

    def test_from_params_empty(self):
        """Test creating empty filters."""
        filters = HeroPerformanceFilters.from_params()
        assert filters.is_empty()

    def test_from_params_with_time_range(self):
        """Test creating filters with time range."""
        filters = HeroPerformanceFilters.from_params(start_time=0, end_time=900)
        assert not filters.is_empty()
        assert filters.time_range is not None
        assert filters.time_range.start == 0
        assert filters.time_range.end == 900

    def test_apply_to_fights_no_filter(self, sample_fights):
        """Empty filters return all fights."""
        filters = HeroPerformanceFilters.from_params()
        result = filters.apply_to_fights(sample_fights)
        assert len(result) == 3

    def test_apply_to_fights_early_game(self, sample_fights):
        """Filter to early game (0-15 min = 0-900 seconds)."""
        filters = HeroPerformanceFilters.from_params(start_time=0, end_time=900)
        result = filters.apply_to_fights(sample_fights)
        assert len(result) == 2
        assert result[0].fight_id == "fight_1"
        assert result[1].fight_id == "fight_2"

    def test_apply_to_fights_mid_game(self, sample_fights):
        """Filter to mid game (15-30 min)."""
        filters = HeroPerformanceFilters.from_params(start_time=900, end_time=1800)
        result = filters.apply_to_fights(sample_fights)
        assert len(result) == 1
        assert result[0].fight_id == "fight_3"

    def test_recalculate_totals(self, sample_fights):
        """Recalculate totals from filtered fights."""
        filters = HeroPerformanceFilters.from_params(start_time=0, end_time=900)
        filtered = filters.apply_to_fights(sample_fights)
        totals = filters.recalculate_totals(filtered)

        assert totals["total_fights"] == 2
        assert totals["total_kills"] == 3  # 1 + 2
        assert totals["total_deaths"] == 1  # 0 + 1
        assert totals["total_assists"] == 1  # 0 + 1
        assert totals["total_teamfights"] == 1  # only fight_2

    def test_recalculate_ability_summary(self, sample_fights):
        """Recalculate ability summary from filtered fights."""
        filters = HeroPerformanceFilters.from_params(start_time=0, end_time=900)
        filtered = filters.apply_to_fights(sample_fights)
        summary = filters.recalculate_ability_summary(filtered)

        # Should have 2 abilities: charge and nether_strike
        assert len(summary) == 2

        # Find charge ability
        charge = next(
            (a for a in summary if "charge" in a.ability.lower()), None
        )
        assert charge is not None
        assert charge.total_casts == 3  # 1 + 2
        assert charge.hero_hits == 4  # 1 + 3

        # Find nether strike
        strike = next(
            (a for a in summary if "nether" in a.ability.lower()), None
        )
        assert strike is not None
        assert strike.total_casts == 1
        assert strike.hero_hits == 1


class TestHeroPerformanceFiltersIntegration:
    """Integration tests using real replay data."""

    def test_earthshaker_early_game_filter(
        self, parsed_replay_data, all_fights
    ):
        """Test filtering Earthshaker performance to early game (match 8461956309)."""
        from src.services.combat.combat_service import CombatService

        cs = CombatService()
        response = cs.get_hero_combat_analysis(
            parsed_replay_data,
            8461956309,
            "earthshaker",
            all_fights.fights,
        )

        assert response.success
        full_match_fights = len(response.fights)

        # Apply early game filter (0-15 min = 0-900 seconds)
        filters = HeroPerformanceFilters.from_params(start_time=0, end_time=900)
        filtered_fights = filters.apply_to_fights(response.fights)
        totals = filters.recalculate_totals(filtered_fights)

        # Early game should have fewer fights than full match
        assert totals["total_fights"] <= full_match_fights
        # Verify totals are recalculated correctly
        assert totals["total_kills"] == sum(f.kills for f in filtered_fights)
        assert totals["total_deaths"] == sum(f.deaths for f in filtered_fights)

    def test_disruptor_ability_summary_filter(
        self, parsed_replay_data, all_fights
    ):
        """Test ability summary recalculation after time filter."""
        from src.services.combat.combat_service import CombatService

        cs = CombatService()
        response = cs.get_hero_combat_analysis(
            parsed_replay_data,
            8461956309,
            "disruptor",
            all_fights.fights,
        )

        assert response.success

        # Get full match ability summary
        full_abilities = {a.ability: a.total_casts for a in response.ability_summary}

        # Apply mid-game filter (15-30 min)
        filters = HeroPerformanceFilters.from_params(start_time=900, end_time=1800)
        filtered_fights = filters.apply_to_fights(response.fights)
        filtered_summary = filters.recalculate_ability_summary(filtered_fights)

        # Filtered abilities should have fewer or equal casts
        for ability in filtered_summary:
            if ability.ability in full_abilities:
                assert ability.total_casts <= full_abilities[ability.ability]
