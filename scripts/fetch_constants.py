#!/usr/bin/env python3
"""
Script to fetch all Dota 2 constants from dotaconstants repository.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.constants_fetcher import constants_fetcher


async def main():
    """Fetch all constants and show summary."""
    
    print("🎮 Fetching Dota 2 Constants from dotaconstants repository...")
    print(f"📁 Storage location: {constants_fetcher.data_dir}")
    print()
    
    # Fetch all constants
    results = await constants_fetcher.fetch_all_constants()
    
    # Show results
    print("\n📊 Fetch Results:")
    print("-" * 50)
    
    successful_files = []
    failed_files = []
    
    for filename, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {filename}")
        
        if success:
            successful_files.append(filename)
        else:
            failed_files.append(filename)
    
    print("-" * 50)
    print(f"✅ Successfully fetched: {len(successful_files)} files")
    if failed_files:
        print(f"❌ Failed to fetch: {len(failed_files)} files")
    
    # Show sample data from heroes.json if available
    if "heroes.json" in successful_files:
        heroes = constants_fetcher.get_heroes_constants()
        if heroes:
            print(f"\n🦸 Heroes Data Sample:")
            print(f"   Total heroes: {len(heroes)}")
            
            # Show first hero as example
            first_hero = list(heroes.values())[0]
            hero_name = first_hero.get("localized_name", "Unknown")
            print(f"   Sample hero: {hero_name}")
            print(f"   Available fields: {list(first_hero.keys())[:8]}...")  # First 8 fields
    
    # Show items sample if available
    if "items.json" in successful_files:
        items = constants_fetcher.get_items_constants()
        if items:
            print(f"\n⚔️  Items Data:")
            print(f"   Total items: {len(items)}")
    
    # Show abilities sample if available  
    if "abilities.json" in successful_files:
        abilities = constants_fetcher.get_abilities_constants()
        if abilities:
            print(f"\n🔥 Abilities Data:")
            print(f"   Total abilities: {len(abilities)}")
    
    print(f"\n🎯 Constants are now cached locally and ready to use!")


if __name__ == "__main__":
    asyncio.run(main())