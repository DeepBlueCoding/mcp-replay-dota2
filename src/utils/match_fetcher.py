"""
Match data fetcher using OpenDota API.
"""

import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)

OPENDOTA_API_URL = "https://api.opendota.com/api"

def get_lane_name(lane: int, is_radiant: bool) -> Optional[str]:
    """
    Convert absolute lane number to team-relative lane name.

    OpenDota lane values: 1=bottom, 2=mid, 3=top, 4=jungle
    Radiant: bottom=safe, top=off
    Dire: top=safe, bottom=off
    """
    if lane == 2:
        return "mid_lane"
    if lane == 4:
        return "jungle"
    if lane == 1:
        return "safe_lane" if is_radiant else "off_lane"
    if lane == 3:
        return "off_lane" if is_radiant else "safe_lane"
    return None


def assign_positions(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign position (1-5) based on lane_role and GPM.

    Position assignment:
    - Pos 1 (carry): safelane core (lane_role=1, higher GPM in lane)
    - Pos 2 (mid): mid lane (lane_role=2)
    - Pos 3 (offlane): offlane core (lane_role=3, higher GPM in lane)
    - Pos 4 (soft support): support with higher GPM
    - Pos 5 (hard support): support with lowest GPM

    Each lane has 2 players - higher GPM is core, lower is support.
    """
    radiant = [p for p in players if p.get("player_slot", 0) < 128]
    dire = [p for p in players if p.get("player_slot", 0) >= 128]

    def process_team(team_players: List[Dict[str, Any]]) -> None:
        lanes: Dict[Any, List[Dict[str, Any]]] = {}
        for player in team_players:
            lane_role = player.get("lane_role")
            if lane_role not in lanes:
                lanes[lane_role] = []
            lanes[lane_role].append(player)

        supports: List[Dict[str, Any]] = []

        for lane_role, lane_players in lanes.items():
            sorted_by_gpm = sorted(
                lane_players,
                key=lambda p: p.get("gold_per_min", 0),
                reverse=True
            )

            if lane_role == 2:
                for p in sorted_by_gpm:
                    p["position"] = 2
                    p["role"] = "core"
            elif lane_role == 1:
                if sorted_by_gpm:
                    sorted_by_gpm[0]["position"] = 1
                    sorted_by_gpm[0]["role"] = "core"
                for p in sorted_by_gpm[1:]:
                    p["role"] = "support"
                    supports.append(p)
            elif lane_role == 3:
                if sorted_by_gpm:
                    sorted_by_gpm[0]["position"] = 3
                    sorted_by_gpm[0]["role"] = "core"
                for p in sorted_by_gpm[1:]:
                    p["role"] = "support"
                    supports.append(p)
            else:
                for p in sorted_by_gpm:
                    p["role"] = "support"
                    supports.append(p)

        supports_sorted = sorted(
            supports,
            key=lambda p: p.get("gold_per_min", 0),
            reverse=True
        )
        for i, p in enumerate(supports_sorted):
            p["position"] = 4 if i == 0 else 5

    process_team(radiant)
    process_team(dire)

    return players


class MatchFetcher:
    """Fetches match data from OpenDota API."""

    async def get_match(self, match_id: int) -> Optional[Dict[str, Any]]:
        """Fetch match data from OpenDota API."""
        url = f"{OPENDOTA_API_URL}/matches/{match_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to fetch match {match_id}: HTTP {response.status}")
                return None

    async def get_players(self, match_id: int) -> List[Dict[str, Any]]:
        """Get player data for a match with lane, role, and position info."""
        match = await self.get_match(match_id)
        if not match:
            return []

        players = match.get("players", [])
        players = assign_positions(players)

        result = []
        for player in players:
            result.append(self._build_player(player))

        return result

    async def get_timeline(self, match_id: int) -> Optional[Dict[str, Any]]:
        """Get time-series data (gold, xp, lh, dn per minute) for all players."""
        match = await self.get_match(match_id)
        if not match:
            return None

        duration_minutes = match.get("duration", 0) // 60

        players = []
        for player in match.get("players", []):
            player_slot = player.get("player_slot", 0)
            is_radiant = player_slot < 128

            players.append({
                "hero_id": player.get("hero_id"),
                "player_slot": player_slot,
                "team": "radiant" if is_radiant else "dire",
                "gold_t": player.get("gold_t", []),
                "xp_t": player.get("xp_t", []),
                "lh_t": player.get("lh_t", []),
                "dn_t": player.get("dn_t", []),
            })

        return {
            "match_id": match_id,
            "duration_minutes": duration_minutes,
            "players": players,
        }

    async def get_player_item_timings(
        self, match_id: int, hero_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get item purchase timings for a specific hero by hero_id.

        Args:
            match_id: The match ID
            hero_id: Hero ID to search for

        Returns:
            List of item purchases with time and item name, sorted by time
        """
        match = await self.get_match(match_id)
        if not match:
            return []

        for player in match.get("players", []):
            if player.get("hero_id") == hero_id:
                purchase_log = player.get("purchase_log")
                if not purchase_log:
                    return []

                return sorted(
                    [
                        {
                            "item": item.get("key", "unknown"),
                            "time": item.get("time", 0),
                        }
                        for item in purchase_log
                    ],
                    key=lambda x: x["time"],
                )

        return []

    def _build_player(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Build player dict with relevant fields."""
        player_slot = player.get("player_slot", 0)
        is_radiant = player_slot < 128
        lane = player.get("lane")

        return {
            "hero_id": player.get("hero_id"),
            "account_id": player.get("account_id"),
            "player_name": player.get("personaname"),
            "pro_name": player.get("name"),
            "player_slot": player_slot,
            "team": "radiant" if is_radiant else "dire",

            "lane": lane,
            "lane_role": player.get("lane_role"),
            "lane_name": get_lane_name(lane, is_radiant) if lane else None,
            "is_roaming": player.get("is_roaming"),
            "role": player.get("role"),
            "position": player.get("position"),

            "kills": player.get("kills"),
            "deaths": player.get("deaths"),
            "assists": player.get("assists"),

            "last_hits": player.get("last_hits"),
            "denies": player.get("denies"),
            "gold_per_min": player.get("gold_per_min"),
            "xp_per_min": player.get("xp_per_min"),
            "net_worth": player.get("net_worth"),
            "level": player.get("level"),

            "hero_damage": player.get("hero_damage"),
            "tower_damage": player.get("tower_damage"),
            "hero_healing": player.get("hero_healing"),

            "item_0": player.get("item_0"),
            "item_1": player.get("item_1"),
            "item_2": player.get("item_2"),
            "item_3": player.get("item_3"),
            "item_4": player.get("item_4"),
            "item_5": player.get("item_5"),
            "item_neutral": player.get("item_neutral"),
        }


match_fetcher = MatchFetcher()
