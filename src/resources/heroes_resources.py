import json
import sys
from pathlib import Path
from typing import Any, Dict
import logging
from src.utils.replay_downloader import ReplayDownloader
from src.utils.constants_fetcher import constants_fetcher

# Add python_manta to path
python_manta_path = Path(__file__).parent.parent.parent.parent / "python_manta" / "src"
sys.path.insert(0, str(python_manta_path))

logger = logging.getLogger(__name__)


class HeroesResource:
    """Resource class for managing Dota 2 hero data using dotaconstants."""
    
    def __init__(self):
        """Initialize the heroes resource."""
        self.replay_downloader = ReplayDownloader()
        self.constants = constants_fetcher
    
    def _convert_constants_to_legacy_format(self, heroes_constants: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Convert dotaconstants hero format to our legacy format for compatibility.
        
        Args:
            heroes_constants: Raw heroes data from dotaconstants
            
        Returns:
            Heroes data in legacy format with npc_ keys
        """
        legacy_heroes = {}
        
        for hero_id, hero_data in heroes_constants.items():
            # Use internal name as key (e.g., "npc_dota_hero_antimage")
            hero_key = hero_data.get("name", f"npc_dota_hero_{hero_id}")
            
            # Convert to legacy format
            legacy_hero = {
                "hero_id": int(hero_id),
                "canonical_name": hero_data.get("localized_name", "Unknown"),
                "attribute": self._map_attribute(hero_data.get("primary_attr", "str")),
                "aliases": self._generate_aliases(hero_data)
            }
            
            legacy_heroes[hero_key] = legacy_hero
        
        return legacy_heroes
    
    def _map_attribute(self, primary_attr: str) -> str:
        """Map dotaconstants attribute format to legacy format."""
        attr_map = {
            "str": "strength",
            "agi": "agility", 
            "int": "intelligence",
            "all": "universal"
        }
        return attr_map.get(primary_attr, "strength")
    
    def _generate_aliases(self, hero_data: Dict[str, Any]) -> list[str]:
        """Generate aliases from hero data."""
        aliases = []
        
        localized_name = hero_data.get("localized_name", "").lower()
        if localized_name:
            aliases.append(localized_name)
            
            # Add common abbreviations and alternative names
            words = localized_name.split()
            if len(words) > 1:
                # Add abbreviation (first letters)
                abbrev = ''.join(word[0] for word in words if word)
                if len(abbrev) > 1:
                    aliases.append(abbrev)
            
            # Add without special characters  
            clean_name = localized_name.replace("-", "").replace("'", "").replace(" ", "")
            if clean_name != localized_name:
                aliases.append(clean_name)
        
        return aliases
    
    def get_all_heroes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all heroes data in legacy format.
        
        Returns:
            Dictionary with hero internal names as keys and hero data as values
        """
        heroes_constants = self.constants.get_heroes_constants()
        
        if not heroes_constants:
            logger.warning("Heroes constants not available, attempting to fetch...")
            # Try to fetch constants if not available
            import asyncio
            try:
                asyncio.run(self.constants.fetch_constants_file("heroes.json"))
                heroes_constants = self.constants.get_heroes_constants()
            except Exception as e:
                logger.error(f"Failed to fetch heroes constants: {e}")
                return {}
        
        if heroes_constants:
            return self._convert_constants_to_legacy_format(heroes_constants)
        
        return {}
    
    def get_heroes_constants_raw(self) -> Dict[str, Dict[str, Any]]:
        """
        Get raw heroes constants data (full dotaconstants format).
        
        Returns:
            Raw heroes data from dotaconstants with all fields
        """
        heroes_constants = self.constants.get_heroes_constants()
        return heroes_constants or {}
    
    def get_heroes_in_match(self, match_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Get heroes data filtered by those playing in a given match.
        Returns data in legacy format but only for the 10 heroes in the match.
        
        Args:
            match_id: The Dota 2 match ID
            
        Returns:
            Dictionary with hero internal names as keys and hero data as values,
            filtered to only include heroes that played in the specified match
        """
        # Download replay if needed
        replay_path = self.replay_downloader.download_replay_sync(match_id)
        
        if not replay_path:
            logger.error(f"Could not download replay for match {match_id}")
            return {}
        
        # Parse the replay to get hero picks
        try:
            from python_manta import parse_demo_draft
            
            draft_info = parse_demo_draft(str(replay_path))
            
            if not draft_info.success:
                logger.error(f"Failed to parse draft for match {match_id}: {draft_info.error}")
                return {}
            
            # Get hero IDs from the draft (only picks, not bans)
            picked_hero_ids = {pick.hero_id for pick in draft_info.picks_bans 
                              if hasattr(pick, 'hero_id') and hasattr(pick, 'is_pick') 
                              and pick.hero_id > 0 and pick.is_pick}
            
            # Get all heroes in legacy format
            all_heroes = self.get_all_heroes()
            
            # Filter to only include picked heroes
            filtered_heroes = {}
            for hero_name, hero_data in all_heroes.items():
                if hero_data.get("hero_id") in picked_hero_ids:
                    filtered_heroes[hero_name] = hero_data
            
            return filtered_heroes
            
        except ImportError:
            logger.error("Draft parser not available. Please ensure python_manta is installed.")
            return {}
        except Exception as e:
            logger.error(f"Error parsing match {match_id}: {e}")
            return {}
    
    def get_heroes_in_match_enriched(self, match_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Get enriched heroes data for a match using full dotaconstants data.
        
        Args:
            match_id: The Dota 2 match ID
            
        Returns:
            Dictionary with hero internal names as keys and enriched hero data as values
        """
        # Download replay if needed
        replay_path = self.replay_downloader.download_replay_sync(match_id)
        
        if not replay_path:
            logger.error(f"Could not download replay for match {match_id}")
            return {}
        
        # Parse the replay to get hero picks
        try:
            from python_manta import parse_demo_draft
            
            draft_info = parse_demo_draft(str(replay_path))
            
            if not draft_info.success:
                logger.error(f"Failed to parse draft for match {match_id}: {draft_info.error}")
                return {}
            
            # Get hero IDs from the draft (only picks, not bans)
            picked_hero_ids = [pick.hero_id for pick in draft_info.picks_bans 
                              if hasattr(pick, 'hero_id') and hasattr(pick, 'is_pick') 
                              and pick.hero_id > 0 and pick.is_pick]
            
            # Enrich with full constants data
            enriched_heroes_list = self.constants.enrich_hero_picks(picked_hero_ids)
            
            # Convert to dictionary with internal names as keys
            enriched_heroes = {}
            for hero_data in enriched_heroes_list:
                hero_key = hero_data.get("name", f"npc_dota_hero_{hero_data.get('id', 'unknown')}")
                enriched_heroes[hero_key] = hero_data
            
            return enriched_heroes
            
        except ImportError:
            logger.error("Draft parser not available. Please ensure python_manta is installed.")
            return {}
        except Exception as e:
            logger.error(f"Error parsing match {match_id}: {e}")
            return {}
    
    def search_heroes_by_role(self, role: str) -> Dict[str, Dict[str, Any]]:
        """
        Search heroes by their role using constants data.
        
        Args:
            role: The role to search for (e.g., "Carry", "Support", "Initiator")
            
        Returns:
            Dictionary of heroes that have the specified role
        """
        heroes_constants = self.get_heroes_constants_raw()
        matching_heroes = {}
        
        for hero_id, hero_data in heroes_constants.items():
            roles = hero_data.get("roles", [])
            if role in roles:
                hero_key = hero_data.get("name", f"npc_dota_hero_{hero_id}")
                matching_heroes[hero_key] = hero_data
        
        return matching_heroes
    
    def get_heroes_by_attribute(self, attribute: str) -> Dict[str, Dict[str, Any]]:
        """
        Get heroes filtered by primary attribute.
        
        Args:
            attribute: Primary attribute ("str", "agi", "int", or "all")
            
        Returns:
            Dictionary of heroes with the specified primary attribute
        """
        heroes_constants = self.get_heroes_constants_raw()
        matching_heroes = {}
        
        for hero_id, hero_data in heroes_constants.items():
            if hero_data.get("primary_attr") == attribute:
                hero_key = hero_data.get("name", f"npc_dota_hero_{hero_id}")
                matching_heroes[hero_key] = hero_data
        
        return matching_heroes


# Create a singleton instance
heroes_resource = HeroesResource()