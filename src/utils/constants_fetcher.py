"""
Constants fetcher utility for downloading and caching Dota 2 constants from dotaconstants repository.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ConstantsFetcher:
    """Utility to fetch and cache Dota 2 constants from the odota/dotaconstants repository."""

    BASE_URL = "https://raw.githubusercontent.com/odota/dotaconstants/master/build"

    # List of all available constants files from dotaconstants
    CONSTANTS_FILES = [
        "heroes.json",
        "items.json",
        "abilities.json",
        "ability_ids.json",
        "game_mode.json",
        "lobby_type.json",
        "region.json",
        "patch.json",
        "permanent_buffs.json",
        "item_ids.json",
        "hero_abilities.json",
        "cluster.json",
        "countries.json",
        "xp_level.json",
        "player_colors.json",
        "chat_wheel.json",
        "neutral_abilities.json",
        "order_types.json",
    ]

    # Mapping from item ability names to item keys (for abilities without dname)
    # Combat log uses ability names like "ability_lamp_use" but items.json uses "panic_button"
    ITEM_ABILITY_TO_ITEM = {
        "ability_lamp_use": "panic_button",  # Magic Lamp
        "ability_pluck_famango": "famango",  # Mango Tree
    }

    # Combat log types from Valve protobuf (DOTA_COMBATLOG_TYPES)
    COMBATLOG_TYPES = {
        -1: "INVALID",
        0: "DAMAGE",
        1: "HEAL",
        2: "MODIFIER_ADD",
        3: "MODIFIER_REMOVE",
        4: "DEATH",
        5: "ABILITY",
        6: "ITEM",
        7: "LOCATION",
        8: "GOLD",
        9: "GAME_STATE",
        10: "XP",
        11: "PURCHASE",
        12: "BUYBACK",
        13: "ABILITY_TRIGGER",
        14: "PLAYERSTATS",
        15: "MULTIKILL",
        16: "KILLSTREAK",
        17: "TEAM_BUILDING_KILL",
        18: "FIRST_BLOOD",
        19: "MODIFIER_STACK_EVENT",
        20: "NEUTRAL_CAMP_STACK",
        21: "PICKUP_RUNE",
        22: "REVEALED_INVISIBLE",
        23: "HERO_SAVED",
        24: "MANA_RESTORED",
        25: "HERO_LEVELUP",
        26: "BOTTLE_HEAL_ALLY",
        27: "ENDGAME_STATS",
        28: "INTERRUPT_CHANNEL",
        29: "ALLIED_GOLD",
        30: "AEGIS_TAKEN",
        31: "MANA_DAMAGE",
        32: "PHYSICAL_DAMAGE_PREVENTED",
        33: "UNIT_SUMMONED",
        34: "ATTACK_EVADE",
        35: "TREE_CUT",
        36: "SUCCESSFUL_SCAN",
        37: "END_KILLSTREAK",
        38: "BLOODSTONE_CHARGE",
        39: "CRITICAL_DAMAGE",
        40: "SPELL_ABSORB",
        41: "UNIT_TELEPORTED",
        42: "KILL_EATER_EVENT",
        43: "NEUTRAL_ITEM_EARNED",
    }

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the constants fetcher.

        Args:
            data_dir: Directory to store constants files. Defaults to project data/constants
        """
        if data_dir:
            self.data_dir = data_dir
        else:
            # Default to data/constants directory
            project_root = Path(__file__).parent.parent.parent
            self.data_dir = project_root / "data" / "constants"

        # Ensure constants directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache for frequently accessed constants
        self._cache: Dict[str, Any] = {}

    async def fetch_constants_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single constants file from the repository.

        Args:
            filename: Name of the constants file (e.g., 'heroes.json')

        Returns:
            Dictionary containing the constants data, or None if fetch failed
        """
        url = f"{self.BASE_URL}/{filename}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                # Save to local file
                local_file = self.data_dir / filename
                with open(local_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"Successfully fetched and cached {filename}")
                return data

        except Exception as e:
            logger.error(f"Failed to fetch {filename}: {e}")
            return None

    async def fetch_all_constants(self) -> Dict[str, bool]:
        """
        Fetch all available constants files from the repository.

        Returns:
            Dictionary mapping filename to success status
        """
        logger.info("Fetching all constants from dotaconstants repository...")
        results = {}

        # Fetch all files concurrently
        tasks = []
        for filename in self.CONSTANTS_FILES:
            task = self.fetch_constants_file(filename)
            tasks.append((filename, task))

        # Wait for all downloads to complete
        for filename, task in tasks:
            try:
                data = await task
                results[filename] = data is not None
            except Exception as e:
                logger.error(f"Error fetching {filename}: {e}")
                results[filename] = False

        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        logger.info(f"Successfully fetched {successful}/{total} constants files")

        return results

    def load_local_constants(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load constants from local cache (with in-memory caching).

        Args:
            filename: Name of the constants file

        Returns:
            Dictionary containing the constants data, or None if not found
        """
        # Check in-memory cache first
        if filename in self._cache:
            return self._cache[filename]

        local_file = self.data_dir / filename

        try:
            if local_file.exists():
                with open(local_file, 'r') as f:
                    data = json.load(f)
                # Store in memory cache
                self._cache[filename] = data
                return data
            else:
                logger.warning(f"Local constants file not found: {filename}")
                return None

        except Exception as e:
            logger.error(f"Failed to load local constants {filename}: {e}")
            return None

    def get_heroes_constants(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get heroes constants from local cache.

        Returns:
            Dictionary with hero IDs as keys and hero data as values
        """
        return self.load_local_constants("heroes.json")

    def get_items_constants(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get items constants from local cache.

        Returns:
            Dictionary with item names as keys and item data as values
        """
        return self.load_local_constants("items.json")

    def get_abilities_constants(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get abilities constants from local cache.

        Returns:
            Dictionary with ability names as keys and ability data as values
        """
        return self.load_local_constants("abilities.json")

    def get_hero_abilities_mapping(self) -> Optional[Dict[str, List[str]]]:
        """
        Get hero abilities mapping from local cache.

        Returns:
            Dictionary mapping hero names to their ability names
        """
        return self.load_local_constants("hero_abilities.json")

    def get_game_modes(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get game modes constants from local cache.

        Returns:
            Dictionary with game mode IDs as keys and mode data as values
        """
        return self.load_local_constants("game_modes.json")

    def convert_hero_by_id(self, hero_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific hero by ID from local heroes constants.

        Args:
            hero_id: The hero ID to look up

        Returns:
            Hero data dictionary or None if not found
        """
        heroes = self.get_heroes_constants()
        if heroes:
            return heroes.get(str(hero_id))
        return None

    def get_hero_name(self, hero_id: int) -> Optional[str]:
        """
        Get hero internal name from hero ID.

        Args:
            hero_id: The hero ID to look up

        Returns:
            Hero internal name (e.g., 'juggernaut') or None if not found
        """
        hero_data = self.convert_hero_by_id(hero_id)
        if hero_data:
            name = hero_data.get("name", "")
            if name.startswith("npc_dota_hero_"):
                return name[14:]
            return name
        return None

    def convert_hero_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific hero by localized name from local constants.

        Args:
            name: The hero's localized name (e.g., "Anti-Mage")

        Returns:
            Hero data dictionary or None if not found
        """
        heroes = self.get_heroes_constants()
        if heroes:
            for hero_data in heroes.values():
                if hero_data.get("localized_name", "").lower() == name.lower():
                    return hero_data
        return None

    def enrich_hero_picks(self, hero_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Enrich a list of hero IDs with comprehensive hero data.

        Args:
            hero_ids: List of hero IDs to enrich

        Returns:
            List of enriched hero data dictionaries
        """
        enriched_heroes = []
        heroes_constants = self.get_heroes_constants()

        if not heroes_constants:
            logger.warning("Heroes constants not available for enrichment")
            return enriched_heroes

        for hero_id in hero_ids:
            hero_data = heroes_constants.get(str(hero_id))
            if hero_data:
                enriched_heroes.append(hero_data)
            else:
                logger.warning(f"Hero ID {hero_id} not found in constants")
                # Add placeholder with just the ID
                enriched_heroes.append({
                    "id": hero_id,
                    "localized_name": f"Unknown Hero {hero_id}",
                    "name": f"npc_dota_hero_{hero_id}"
                })

        return enriched_heroes

    async def update_constants_if_needed(self, max_age_hours: int = 24) -> bool:
        """
        Update constants if they're older than specified age.

        Args:
            max_age_hours: Maximum age in hours before updating

        Returns:
            True if constants were updated, False otherwise
        """
        heroes_file = self.data_dir / "heroes.json"

        # Check if we need to update
        if heroes_file.exists():
            import time
            file_age_hours = (time.time() - heroes_file.stat().st_mtime) / 3600
            if file_age_hours < max_age_hours:
                logger.info(f"Constants are fresh (age: {file_age_hours:.1f}h), skipping update")
                return False

        # Update constants
        logger.info("Updating constants...")
        results = await self.fetch_all_constants()
        return any(results.values())

    def list_available_constants(self) -> List[str]:
        """
        List all locally available constants files.

        Returns:
            List of available constants filenames
        """
        available = []
        for filename in self.CONSTANTS_FILES:
            local_file = self.data_dir / filename
            if local_file.exists():
                available.append(filename)
        return available

    def get_combatlog_type_name(self, type_id: int) -> str:
        """Get combat log type name from ID."""
        return self.COMBATLOG_TYPES.get(type_id, f"UNKNOWN_{type_id}")

    def get_item_ids_mapping(self) -> Optional[Dict[str, str]]:
        """Get item ID to internal name mapping."""
        return self.load_local_constants("item_ids.json")

    def get_item_name(self, item_id: int) -> Optional[str]:
        """
        Get human-readable item name from item ID.

        Args:
            item_id: The item ID (e.g., 1 for Blink Dagger)

        Returns:
            Human-readable item name (e.g., "Blink Dagger") or None if not found
        """
        if not item_id or item_id == 0:
            return None

        item_ids = self.get_item_ids_mapping()
        if not item_ids:
            return None

        internal_name = item_ids.get(str(item_id))
        if not internal_name:
            return None

        items = self.get_items_constants()
        if not items:
            return internal_name

        item_data = items.get(internal_name)
        if item_data:
            return item_data.get("dname", internal_name)

        return internal_name

    def convert_item_ids_to_names(self, item_ids: List[Optional[int]]) -> List[str]:
        """
        Convert a list of item IDs to human-readable names.

        Args:
            item_ids: List of item IDs (can contain None or 0 for empty slots)

        Returns:
            List of item names (empty string for empty slots)
        """
        return [self.get_item_name(item_id) or "" for item_id in item_ids]

    def get_display_name(self, internal_name: Optional[str]) -> Optional[str]:
        """
        Convert internal item/ability name to human-readable display name.

        Handles:
        - Item names: "item_bfury" -> "Battle Fury"
        - Ability names: "nevermore_shadowraze1" -> "Shadowraze"
        - Special cases: "dota_unknown" -> "attack", None -> None

        Args:
            internal_name: Internal name from combat log (e.g., "item_bfury", "nevermore_shadowraze1")

        Returns:
            Human-readable display name, or original name if no translation found
        """
        if not internal_name:
            return None

        if internal_name == "dota_unknown":
            return "attack"

        # Handle item names (item_<name>)
        if internal_name.startswith("item_"):
            item_key = internal_name[5:]  # Remove "item_" prefix
            items = self.get_items_constants()
            if items and item_key in items:
                return items[item_key].get("dname", internal_name)
            return internal_name

        # Handle ability names
        abilities = self.get_abilities_constants()
        if abilities and internal_name in abilities:
            dname = abilities[internal_name].get("dname")
            if dname:
                return dname

        # Check if this is an item ability that maps to an item
        if internal_name in self.ITEM_ABILITY_TO_ITEM:
            item_key = self.ITEM_ABILITY_TO_ITEM[internal_name]
            items = self.get_items_constants()
            if items and item_key in items:
                return items[item_key].get("dname", internal_name)

        return internal_name


# Create a singleton instance
constants_fetcher = ConstantsFetcher()
