"""
Tests for FightService.

Uses pre-parsed replay data from conftest.py fixtures.
All data is from match 8461956309 with verified values from Dotabuff.
"""

from src.services.combat.fight_service import FightService
from src.services.models.combat_data import Fight, HeroDeath


class TestFightDetection:

    def test_get_fight_at_time_returns_fight_model(self, fight_first_blood):
        assert isinstance(fight_first_blood, Fight)

    def test_first_blood_fight_has_correct_killer_and_victim(self, fight_first_blood):
        # v2 FightDetector only tracks killer/victim from deaths, not nearby combatants
        assert "earthshaker" in fight_first_blood.participants
        assert "disruptor" in fight_first_blood.participants

    def test_first_blood_fight_found(self, fight_first_blood):
        # Verify the fight was detected at the correct time
        assert fight_first_blood is not None
        assert len(fight_first_blood.deaths) >= 1

    def test_fight_detection_separates_concurrent_fights(self, fight_first_blood, fight_pango_nevermore):
        # First blood fight shouldn't include heroes from pango/nevermore fight
        assert "pangolier" not in fight_first_blood.participants or "nevermore" not in fight_first_blood.participants

    def test_pango_nevermore_fight_found(self, fight_pango_nevermore):
        # Verify pangolier fight was detected
        assert fight_pango_nevermore is not None
        assert "pangolier" in fight_pango_nevermore.participants
        assert "nevermore" in fight_pango_nevermore.participants

    def test_fight_has_deaths(self, fight_first_blood):
        assert len(fight_first_blood.deaths) > 0
        assert all(isinstance(d, HeroDeath) for d in fight_first_blood.deaths)

    def test_fight_without_hero_anchor_finds_nearest_fight(self, fight_first_blood_no_hero):
        assert isinstance(fight_first_blood_no_hero, Fight)
        assert "earthshaker" in fight_first_blood_no_hero.participants
        assert len(fight_first_blood_no_hero.deaths) > 0


class TestFightSummary:
    """Tests for get_fight_summary() - used by list_fights tool. Match 8461956309."""

    def test_fight_summary_total_fights(self, parsed_replay_data):
        """Match 8461956309 has 24 fights detected."""
        service = FightService()
        summary = service.get_fight_summary(parsed_replay_data)
        assert summary["total_fights"] == 24

    def test_fight_summary_total_deaths(self, parsed_replay_data):
        """Match 8461956309 has 31 hero deaths."""
        service = FightService()
        summary = service.get_fight_summary(parsed_replay_data)
        assert summary["total_deaths"] == 31

    def test_first_fight_is_first_blood(self, parsed_replay_data):
        """First fight should be first blood: Disruptor kills Earthshaker at 4:48."""
        service = FightService()
        summary = service.get_fight_summary(parsed_replay_data)

        first_fight = summary["fights"][0]
        assert first_fight["fight_id"] == "fight_1"
        assert first_fight["start_time_str"] == "4:48"
        assert first_fight["total_deaths"] == 1
        assert "earthshaker" in first_fight["participants"]
        assert "disruptor" in first_fight["participants"]

    def test_first_fight_death_details(self, parsed_replay_data):
        """First blood death: Disruptor kills Earthshaker with thunder_strike."""
        service = FightService()
        summary = service.get_fight_summary(parsed_replay_data)

        first_fight = summary["fights"][0]
        assert len(first_fight["deaths"]) == 1

        death = first_fight["deaths"][0]
        assert death["victim"] == "earthshaker"
        assert death["killer"] == "disruptor"
        assert "thunder_strike" in death["ability"]

    def test_fight_deaths_is_list_not_int(self, parsed_replay_data):
        """Regression: deaths must be list, was returning int causing 'int not iterable'."""
        service = FightService()
        summary = service.get_fight_summary(parsed_replay_data)

        # Check all fights have deaths as list
        for fight in summary["fights"]:
            assert isinstance(fight["deaths"], list), (
                f"Fight {fight['fight_id']}: deaths should be list, got {type(fight['deaths'])}"
            )
