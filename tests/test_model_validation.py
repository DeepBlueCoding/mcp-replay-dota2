"""Tests for Pydantic model validation to catch type errors early."""

import pytest
from pydantic import ValidationError

from src.models.pro_scene import (
    ProMatchSummary,
)
from src.models.tool_responses import (
    HeroStats,
    MatchHeroesResponse,
    MatchPlayerInfo,
)
from src.utils.constants_fetcher import constants_fetcher


class TestHeroStatsValidation:
    """Tests for HeroStats model validation."""

    def test_hero_stats_with_string_items(self):
        """HeroStats should accept string item names."""
        hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5,
            deaths=2,
            assists=10,
            last_hits=300,
            denies=20,
            gpm=650,
            xpm=700,
            net_worth=25000,
            hero_damage=15000,
            tower_damage=3000,
            hero_healing=0,
            items=["Power Treads", "Battle Fury", "Manta Style", "Abyssal Blade", "Butterfly", ""],
            item_neutral="Paladin Sword",
        )

        assert hero.hero_id == 1
        assert hero.items[0] == "Power Treads"
        assert hero.items[5] == ""
        assert hero.item_neutral == "Paladin Sword"

    def test_hero_stats_with_empty_items(self):
        """HeroStats should handle empty item slots."""
        hero = HeroStats(
            hero_id=2,
            hero_name="npc_dota_hero_axe",
            localized_name="Axe",
            team="dire",
            kills=3,
            deaths=5,
            assists=15,
            last_hits=150,
            denies=5,
            gpm=400,
            xpm=450,
            net_worth=12000,
            hero_damage=10000,
            tower_damage=1000,
            hero_healing=0,
            items=["", "", "", "", "", ""],
            item_neutral=None,
        )

        assert all(item == "" for item in hero.items)
        assert hero.item_neutral is None

    def test_hero_stats_rejects_integer_items(self):
        """HeroStats should reject integer item IDs - they must be converted to names."""
        with pytest.raises(ValidationError):
            HeroStats(
                hero_id=1,
                hero_name="npc_dota_hero_antimage",
                localized_name="Anti-Mage",
                team="radiant",
                kills=5,
                deaths=2,
                assists=10,
                last_hits=300,
                denies=20,
                gpm=650,
                xpm=700,
                net_worth=25000,
                hero_damage=15000,
                tower_damage=3000,
                hero_healing=0,
                items=[208, 65, 147, 0, 0, 0],  # Integer IDs should fail
            )

    def test_hero_stats_team_literal(self):
        """HeroStats team must be 'radiant' or 'dire'."""
        with pytest.raises(ValidationError):
            HeroStats(
                hero_id=1,
                hero_name="npc_dota_hero_antimage",
                localized_name="Anti-Mage",
                team="invalid_team",  # Should fail
                kills=0,
                deaths=0,
                assists=0,
                last_hits=0,
                denies=0,
                gpm=0,
                xpm=0,
                net_worth=0,
                hero_damage=0,
                tower_damage=0,
                hero_healing=0,
                items=[],
            )


class TestMatchHeroesResponseValidation:
    """Tests for MatchHeroesResponse model validation."""

    def test_match_heroes_response_success(self):
        """MatchHeroesResponse should accept valid hero lists."""
        radiant_hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5,
            deaths=2,
            assists=10,
            last_hits=300,
            denies=20,
            gpm=650,
            xpm=700,
            net_worth=25000,
            hero_damage=15000,
            tower_damage=3000,
            hero_healing=0,
            items=["Power Treads", "Battle Fury", "", "", "", ""],
        )

        response = MatchHeroesResponse(
            success=True,
            match_id=8188461851,
            radiant_heroes=[radiant_hero],
            dire_heroes=[],
        )

        assert response.success is True
        assert response.match_id == 8188461851
        assert len(response.radiant_heroes) == 1

    def test_match_heroes_response_error(self):
        """MatchHeroesResponse should handle error state."""
        response = MatchHeroesResponse(
            success=False,
            match_id=12345,
            error="Match not found",
        )

        assert response.success is False
        assert response.error == "Match not found"
        assert response.radiant_heroes == []
        assert response.dire_heroes == []


class TestMatchPlayerInfoValidation:
    """Tests for MatchPlayerInfo model validation."""

    def test_match_player_info_creation(self):
        """MatchPlayerInfo should accept valid player data."""
        player = MatchPlayerInfo(
            player_name="TestPlayer",
            pro_name="ProName",
            account_id=123456789,
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
        )

        assert player.player_name == "TestPlayer"
        assert player.pro_name == "ProName"
        assert player.hero_id == 1

    def test_match_player_info_optional_fields(self):
        """MatchPlayerInfo should handle optional fields."""
        player = MatchPlayerInfo(
            player_name="Anonymous",
            hero_id=2,
            hero_name="npc_dota_hero_axe",
            localized_name="Axe",
        )

        assert player.pro_name is None
        assert player.account_id is None


class TestProMatchSummaryValidation:
    """Tests for ProMatchSummary model validation."""

    def test_pro_match_summary_with_team_names(self):
        """ProMatchSummary should accept team names as strings."""
        match = ProMatchSummary(
            match_id=8188461851,
            radiant_team_id=8261500,
            radiant_team_name="Xtreme Gaming",
            dire_team_id=8599101,
            dire_team_name="Team Spirit",
            radiant_win=True,
            duration=2400,
            start_time=1733580000,
        )

        assert match.radiant_team_name == "Xtreme Gaming"
        assert match.dire_team_name == "Team Spirit"

    def test_pro_match_summary_with_null_team_names(self):
        """ProMatchSummary should accept null team names."""
        match = ProMatchSummary(
            match_id=8188461852,
            radiant_team_id=8261500,
            radiant_team_name=None,
            dire_team_id=8599101,
            dire_team_name=None,
            radiant_win=False,
            duration=2200,
            start_time=1733580100,
        )

        assert match.radiant_team_name is None
        assert match.dire_team_name is None


class TestItemConversion:
    """Tests for item ID to name conversion."""

    def test_get_item_name_blink_dagger(self):
        """Item ID 1 should resolve to Blink Dagger."""
        name = constants_fetcher.get_item_name(1)
        assert name == "Blink Dagger"

    def test_get_item_name_power_treads(self):
        """Item ID 63 should resolve to Power Treads."""
        name = constants_fetcher.get_item_name(63)
        assert name == "Power Treads"

    def test_get_item_name_zero_returns_none(self):
        """Item ID 0 (empty slot) should return None."""
        name = constants_fetcher.get_item_name(0)
        assert name is None

    def test_get_item_name_none_returns_none(self):
        """Item ID None should return None."""
        name = constants_fetcher.get_item_name(None)
        assert name is None

    def test_convert_item_ids_to_names(self):
        """convert_item_ids_to_names should convert a list of IDs to names."""
        item_ids = [1, 63, 0, None, 208, 0]
        names = constants_fetcher.convert_item_ids_to_names(item_ids)

        assert len(names) == 6
        assert names[0] == "Blink Dagger"
        assert names[1] == "Power Treads"
        assert names[2] == ""  # 0 = empty
        assert names[3] == ""  # None = empty
        assert isinstance(names[4], str)  # Should be a string item name
        assert names[5] == ""  # 0 = empty

    def test_convert_item_ids_all_empty(self):
        """convert_item_ids_to_names should handle all empty slots."""
        item_ids = [0, 0, 0, None, 0, 0]
        names = constants_fetcher.convert_item_ids_to_names(item_ids)

        assert all(name == "" for name in names)

    def test_item_conversion_produces_valid_hero_stats(self):
        """Item conversion should produce strings that pass HeroStats validation."""
        item_ids = [1, 63, 208, 0, 0, 0]
        item_names = constants_fetcher.convert_item_ids_to_names(item_ids)

        hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5,
            deaths=2,
            assists=10,
            last_hits=300,
            denies=20,
            gpm=650,
            xpm=700,
            net_worth=25000,
            hero_damage=15000,
            tower_damage=3000,
            hero_healing=0,
            items=item_names,
            item_neutral=constants_fetcher.get_item_name(676),
        )

        assert all(isinstance(item, str) for item in hero.items)
