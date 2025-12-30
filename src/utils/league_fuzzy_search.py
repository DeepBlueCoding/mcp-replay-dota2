"""Fuzzy search utility for leagues/tournaments."""

import logging
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from src.models.pro_scene import SearchResult

logger = logging.getLogger(__name__)

LEAGUE_ALIASES = {
    "ti": ["the international", "ti"],
    "the international": ["ti", "the international"],
    "esl": ["esl one", "esl"],
    "dpc": ["dota pro circuit", "dpc"],
    "dreamleague": ["dreamleague", "dream league"],
    "blast": ["blast slam", "blast"],
    "slam": ["blast slam", "slam"],
    "riyadh": ["riyadh masters", "riyadh"],
    "bali": ["bali major", "bali"],
}


class LeagueFuzzySearch:
    """Fuzzy search for leagues using OpenDota data."""

    def __init__(self) -> None:
        self._leagues: List[Dict[str, Any]] = []
        self._initialized: bool = False

    def initialize(self, leagues: List[Dict[str, Any]]) -> None:
        """Initialize with league data."""
        self._leagues = leagues
        self._initialized = True
        logger.info(f"Initialized league fuzzy search with {len(leagues)} leagues")

    def _expand_aliases(self, search_term: str) -> List[str]:
        """Expand search term with known aliases."""
        search_lower = search_term.lower().strip()
        expansions = [search_lower]

        for alias, expanded_list in LEAGUE_ALIASES.items():
            if search_lower.startswith(alias + " "):
                rest = search_lower[len(alias) + 1:]
                for exp in expanded_list:
                    if exp != alias:
                        expansions.append(f"{exp} {rest}")
            elif alias in search_lower:
                for exp in expanded_list:
                    if exp != alias:
                        expansions.append(search_lower.replace(alias, exp))

        return list(set(expansions))

    def _calculate_similarity(self, search_term: str, target: str) -> float:
        """Calculate similarity between search term and target string."""
        search_lower = search_term.lower().strip()
        target_lower = target.lower().strip()

        if search_lower == target_lower:
            return 1.0

        if search_lower in target_lower:
            len_ratio = len(search_lower) / len(target_lower)
            return 0.85 + (0.1 * len_ratio)
        elif target_lower in search_lower:
            return 0.75

        return SequenceMatcher(None, search_lower, target_lower).ratio()

    def search(
        self, query: str, threshold: float = 0.5, max_results: int = 10
    ) -> List[SearchResult]:
        """Search for leagues using fuzzy matching with alias expansion."""
        if not self._initialized:
            logger.warning("League fuzzy search not initialized")
            return []

        if not query or not query.strip():
            return []

        expansions = self._expand_aliases(query)
        matches = []

        for league in self._leagues:
            league_id = league.get("leagueid")
            if not league_id:
                continue

            league_name = league.get("name") or "Unknown"

            best_score = 0.0
            for exp in expansions:
                score = self._calculate_similarity(exp, league_name)
                if score > best_score:
                    best_score = score

            if best_score >= threshold:
                matches.append(
                    SearchResult(
                        id=league_id,
                        name=league_name,
                        matched_alias=query,
                        similarity=best_score,
                    )
                )

        matches.sort(key=lambda x: x.similarity, reverse=True)
        return matches[:max_results]

    def find_best_match(
        self, query: str, threshold: float = 0.5
    ) -> Optional[SearchResult]:
        """Find the single best matching league."""
        matches = self.search(query, threshold, max_results=1)
        return matches[0] if matches else None

    def matches_league(self, query: str, league_name: str, threshold: float = 0.5) -> bool:
        """Check if query matches a specific league name."""
        if not league_name:
            return False

        expansions = self._expand_aliases(query)
        for exp in expansions:
            score = self._calculate_similarity(exp, league_name)
            if score >= threshold:
                return True

        return False


league_fuzzy_search = LeagueFuzzySearch()
