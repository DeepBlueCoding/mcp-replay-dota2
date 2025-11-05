"""
Test suite for heroes_resources.py

Following CLAUDE.md testing principles:
- Test against REAL EXPECTED VALUES from actual data
- Use Golden Master approach with verified values
- Test business logic correctness with real inputs
- No framework behavior testing, only actual business value
"""

import pytest
from pathlib import Path
from src.resources.heroes_resources import HeroesResource

# Real test data - these are VERIFIED values from actual dotaconstants
EXPECTED_TOTAL_HEROES = 126  # Actual count from dotaconstants

# Known heroes with their exact data for golden master testing (from dotaconstants)
KNOWN_ABADDON_DATA = {
    "hero_id": 102,
    "canonical_name": "Abaddon",
    "aliases": ["abaddon"],
    "attribute": "universal"
}

KNOWN_ANTI_MAGE_DATA = {
    "hero_id": 1,
    "canonical_name": "Anti-Mage",
    "aliases": ["anti-mage", "antimage"],
    "attribute": "agility"
}

KNOWN_ZEUS_DATA = {
    "hero_id": 22,
    "canonical_name": "Zeus", 
    "aliases": ["zeus"],
    "attribute": "intelligence"
}

# Expected hero internal names for specific heroes (from dotaconstants)
EXPECTED_ABADDON_KEY = "npc_dota_hero_abaddon"
EXPECTED_ANTI_MAGE_KEY = "npc_dota_hero_antimage"
EXPECTED_ZEUS_KEY = "npc_dota_hero_zuus"


class TestHeroesResource:
    """Test suite for HeroesResource business logic."""
    
    @pytest.fixture
    def heroes_resource(self):
        """Fixture that provides a HeroesResource instance."""
        return HeroesResource()
    
    def test_heroes_constants_loads_successfully(self, heroes_resource):
        """Test that heroes constants loads from dotaconstants."""
        # ACT: Get the raw heroes constants
        heroes_constants = heroes_resource.get_heroes_constants_raw()
        
        # ASSERT: Data is loaded and has expected structure
        assert isinstance(heroes_constants, dict)
        assert len(heroes_constants) > 0
    
    def test_get_all_heroes_returns_exact_count(self, heroes_resource):
        """Test that get_all_heroes returns the exact expected count."""
        # ACT: Get all heroes
        all_heroes = heroes_resource.get_all_heroes()
        
        # ASSERT: Returns exactly 123 heroes (verified count from real data)
        assert len(all_heroes) == EXPECTED_TOTAL_HEROES
    
    def test_get_all_heroes_contains_known_heroes(self, heroes_resource):
        """Test that get_all_heroes contains known heroes with exact data."""
        # ACT: Get all heroes
        all_heroes = heroes_resource.get_all_heroes()
        
        # ASSERT: Contains Abaddon with exact expected data
        assert EXPECTED_ABADDON_KEY in all_heroes
        abaddon = all_heroes[EXPECTED_ABADDON_KEY]
        assert abaddon == KNOWN_ABADDON_DATA
        
        # ASSERT: Contains Anti-Mage with exact expected data
        assert EXPECTED_ANTI_MAGE_KEY in all_heroes
        anti_mage = all_heroes[EXPECTED_ANTI_MAGE_KEY]
        assert anti_mage == KNOWN_ANTI_MAGE_DATA
        
        # ASSERT: Contains Zeus with exact expected data
        assert EXPECTED_ZEUS_KEY in all_heroes
        zeus = all_heroes[EXPECTED_ZEUS_KEY]
        assert zeus == KNOWN_ZEUS_DATA
    
    def test_get_all_heroes_has_all_required_attributes(self, heroes_resource):
        """Test that every hero has all required attributes."""
        # ACT: Get all heroes
        all_heroes = heroes_resource.get_all_heroes()
        
        # ASSERT: Every hero has required fields
        for hero_key, hero_data in all_heroes.items():
            assert "hero_id" in hero_data
            assert "canonical_name" in hero_data
            assert "aliases" in hero_data
            assert "attribute" in hero_data
            
            # ASSERT: Hero IDs are positive integers
            assert isinstance(hero_data["hero_id"], int)
            assert hero_data["hero_id"] > 0
            
            # ASSERT: Canonical names are non-empty strings
            assert isinstance(hero_data["canonical_name"], str)
            assert len(hero_data["canonical_name"]) > 0
            
            # ASSERT: Aliases are non-empty lists
            assert isinstance(hero_data["aliases"], list)
            assert len(hero_data["aliases"]) > 0
            
            # ASSERT: Attribute is one of the four valid types (including universal)
            assert hero_data["attribute"] in ["strength", "agility", "intelligence", "universal"]
    
    def test_get_all_heroes_returns_copy_not_reference(self, heroes_resource):
        """Test that get_all_heroes returns a copy, not the original data."""
        # ARRANGE: Get heroes twice
        heroes1 = heroes_resource.get_all_heroes()
        heroes2 = heroes_resource.get_all_heroes()
        
        # ASSERT: They are equal in content but different objects
        assert heroes1 == heroes2
        assert heroes1 is not heroes2
        
        # ARRANGE: Modify one copy
        heroes1["test_key"] = {"test": "data"}
        
        # ASSERT: Original data is not modified
        heroes3 = heroes_resource.get_all_heroes()
        assert "test_key" not in heroes3
    
    def test_all_hero_ids_are_unique(self, heroes_resource):
        """Test that all heroes have unique IDs."""
        # ACT: Get all heroes
        all_heroes = heroes_resource.get_all_heroes()
        
        # ARRANGE: Extract all hero IDs
        hero_ids = [hero_data["hero_id"] for hero_data in all_heroes.values()]
        
        # ASSERT: All hero IDs are unique (no duplicates)
        assert len(hero_ids) == len(set(hero_ids))
    
    def test_attribute_distribution_is_realistic(self, heroes_resource):
        """Test that hero attribute distribution matches expected ranges."""
        # ACT: Get all heroes
        all_heroes = heroes_resource.get_all_heroes()
        
        # ARRANGE: Count heroes by attribute
        attribute_counts = {"strength": 0, "agility": 0, "intelligence": 0, "universal": 0}
        for hero_data in all_heroes.values():
            attribute_counts[hero_data["attribute"]] += 1
        
        # ASSERT: Each attribute has reasonable number of heroes (based on real dotaconstants data)
        assert attribute_counts["strength"] == 35  # Exact count from constants
        assert attribute_counts["agility"] == 34   # Exact count from constants  
        assert attribute_counts["intelligence"] == 34  # Exact count from constants
        assert attribute_counts["universal"] == 23  # Exact count from constants
        
        # ASSERT: Total adds up to expected count
        total_by_attribute = sum(attribute_counts.values())
        assert total_by_attribute == EXPECTED_TOTAL_HEROES
    
    def test_heroes_have_realistic_aliases(self, heroes_resource):
        """Test that heroes have realistic alias patterns."""
        # ACT: Get all heroes
        all_heroes = heroes_resource.get_all_heroes()
        
        for hero_key, hero_data in all_heroes.items():
            aliases = hero_data["aliases"]
            canonical_name = hero_data["canonical_name"]
            
            # ASSERT: First alias is usually lowercase version of canonical name
            first_alias = aliases[0].lower()
            canonical_lower = canonical_name.lower()
            
            # For most heroes, first alias matches canonical name
            # Allow some exceptions for heroes with complex names
            if " " not in canonical_name:
                assert first_alias == canonical_lower or canonical_lower.startswith(first_alias)


class TestHeroesResourceWithRealMatch:
    """Test suite for match-specific hero functionality with real match data."""
    
    @pytest.fixture 
    def heroes_resource(self):
        """Fixture that provides a HeroesResource instance."""
        return HeroesResource()
    
    # Using the same match ID we tested before: 8461956309
    REAL_MATCH_ID = 8461956309
    
    # These are the EXACT heroes we verified were picked in this real match (dotaconstants internal names)
    EXPECTED_MATCH_HEROES = {
        "npc_dota_hero_earthshaker",
        "npc_dota_hero_magnataur",  # Magnus internal name in constants 
        "npc_dota_hero_juggernaut",
        "npc_dota_hero_medusa",
        "npc_dota_hero_naga_siren",
        "npc_dota_hero_pangolier",
        "npc_dota_hero_nevermore",  # Shadow Fiend internal name in constants
        "npc_dota_hero_disruptor",
        "npc_dota_hero_pugna",
        "npc_dota_hero_shadow_demon"
    }
    
    @pytest.mark.integration
    def test_get_heroes_in_match_returns_exactly_ten_heroes(self, heroes_resource):
        """Test that get_heroes_in_match returns exactly 10 heroes for a real match."""
        # ACT: Get heroes for real match
        match_heroes = heroes_resource.get_heroes_in_match(self.REAL_MATCH_ID)
        
        # ASSERT: Returns exactly 10 heroes (5 per team)
        assert len(match_heroes) == 10
    
    @pytest.mark.integration
    def test_get_heroes_in_match_returns_expected_heroes(self, heroes_resource):
        """Test that get_heroes_in_match returns the exact expected heroes."""
        # ACT: Get heroes for real match
        match_heroes = heroes_resource.get_heroes_in_match(self.REAL_MATCH_ID)
        
        # ARRANGE: Extract hero keys
        returned_hero_keys = set(match_heroes.keys())
        
        # ASSERT: Returns exactly the expected heroes from our golden master data
        assert returned_hero_keys == self.EXPECTED_MATCH_HEROES
    
    @pytest.mark.integration
    def test_get_heroes_in_match_preserves_data_format(self, heroes_resource):
        """Test that match heroes have the same format as all heroes."""
        # ARRANGE: Get both all heroes and match heroes
        all_heroes = heroes_resource.get_all_heroes()
        match_heroes = heroes_resource.get_heroes_in_match(self.REAL_MATCH_ID)
        
        # ACT: Compare structure for overlapping heroes
        for hero_key in match_heroes.keys():
            match_hero = match_heroes[hero_key]
            all_hero = all_heroes[hero_key]
            
            # ASSERT: Data is identical
            assert match_hero == all_hero
            
            # ASSERT: Has all required fields
            assert "hero_id" in match_hero
            assert "canonical_name" in match_hero
            assert "aliases" in match_hero
            assert "attribute" in match_hero
    
    def test_get_heroes_in_match_with_invalid_match_id(self, heroes_resource):
        """Test error handling with invalid match ID."""
        # ACT: Try to get heroes for non-existent match
        invalid_match_heroes = heroes_resource.get_heroes_in_match(999999999)
        
        # ASSERT: Returns empty dict for invalid match
        assert invalid_match_heroes == {}
    
    @pytest.mark.integration 
    def test_match_heroes_contain_expected_specific_heroes(self, heroes_resource):
        """Test that specific known heroes appear in the match with correct data."""
        # ACT: Get heroes for real match
        match_heroes = heroes_resource.get_heroes_in_match(self.REAL_MATCH_ID)
        
        # ASSERT: Earthshaker is in the match with correct data
        assert "npc_dota_hero_earthshaker" in match_heroes
        earthshaker = match_heroes["npc_dota_hero_earthshaker"]
        assert earthshaker["hero_id"] == 7
        assert earthshaker["canonical_name"] == "Earthshaker"
        assert earthshaker["attribute"] == "strength"
        
        # ASSERT: Juggernaut is in the match with correct data
        assert "npc_dota_hero_juggernaut" in match_heroes
        juggernaut = match_heroes["npc_dota_hero_juggernaut"]
        assert juggernaut["hero_id"] == 8
        assert juggernaut["canonical_name"] == "Juggernaut"
        assert juggernaut["attribute"] == "agility"
        
        # ASSERT: Pugna is in the match with correct data
        assert "npc_dota_hero_pugna" in match_heroes
        pugna = match_heroes["npc_dota_hero_pugna"]
        assert pugna["hero_id"] == 45
        assert pugna["canonical_name"] == "Pugna"
        assert pugna["attribute"] == "intelligence"


class TestHeroesResourceErrorHandling:
    """Test suite for error handling scenarios."""
    
    def test_resource_handles_missing_constants(self):
        """Test that resource handles missing constants gracefully."""
        # ARRANGE: Create resource and simulate missing constants
        resource = HeroesResource()
        # Mock constants fetcher to return empty data
        resource.constants.get_heroes_constants = lambda: None
        
        # ACT: Try to get heroes data
        heroes_data = resource.get_all_heroes()
        
        # ASSERT: Returns empty dict on error
        assert heroes_data == {}
    
    
    def test_get_all_heroes_with_empty_constants(self):
        """Test get_all_heroes behavior with empty constants data."""
        # ARRANGE: Create resource with mocked empty constants
        resource = HeroesResource()
        resource.constants.get_heroes_constants = lambda: None
        
        # ACT: Get all heroes from empty resource
        all_heroes = resource.get_all_heroes()
        
        # ASSERT: Returns empty dict
        assert all_heroes == {}
    
    def test_get_heroes_in_match_with_empty_constants(self):
        """Test get_heroes_in_match behavior with empty constants data."""
        # ARRANGE: Create resource with mocked empty constants
        resource = HeroesResource()
        resource.constants.get_heroes_constants = lambda: None
        
        # ACT: Try to get match heroes with empty data
        match_heroes = resource.get_heroes_in_match(123456)
        
        # ASSERT: Returns empty dict (no heroes to match)
        assert match_heroes == {}