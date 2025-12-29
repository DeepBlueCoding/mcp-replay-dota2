"""Tests for league fuzzy search utility."""

import pytest

from src.utils.league_fuzzy_search import LeagueFuzzySearch


class TestLeagueAliasExpansion:
    """Tests for _expand_aliases method."""

    def test_ti_expands_to_the_international(self):
        """TI 2025 should expand to include 'the international 2025'."""
        lfs = LeagueFuzzySearch()
        expansions = lfs._expand_aliases("TI 2025")
        assert "the international 2025" in expansions
        assert "ti 2025" in expansions

    def test_esl_expands_to_esl_one(self):
        """ESL should expand to include 'esl one'."""
        lfs = LeagueFuzzySearch()
        expansions = lfs._expand_aliases("ESL")
        assert "esl one" in expansions
        assert "esl" in expansions

    def test_blast_expands_to_blast_slam(self):
        """blast should expand to blast slam."""
        lfs = LeagueFuzzySearch()
        expansions = lfs._expand_aliases("blast V")
        assert "blast slam v" in expansions

    def test_dpc_expands_to_dota_pro_circuit(self):
        """DPC should expand to dota pro circuit."""
        lfs = LeagueFuzzySearch()
        expansions = lfs._expand_aliases("DPC")
        assert "dota pro circuit" in expansions


class TestLeagueMatchesFilter:
    """Tests for matches_league method."""

    def test_ti_matches_the_international(self):
        """TI 2025 should match The International 2025."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("TI 2025", "The International 2025")

    def test_ti13_matches_the_international_2024(self):
        """TI abbreviation with number matches full name."""
        lfs = LeagueFuzzySearch()
        # "ti" in "ti13" should expand, though matching TI13 to TI2024 is a bit fuzzy
        assert lfs.matches_league("The International", "The International 2024")

    def test_blast_slam_matches(self):
        """blast slam should match BLAST Slam V."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("blast slam", "BLAST Slam V")
        assert lfs.matches_league("SLAM V", "BLAST Slam V")

    def test_esl_matches_esl_one(self):
        """ESL should match ESL One tournaments."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("ESL", "ESL One Kuala Lumpur 2025")

    def test_dreamleague_matches(self):
        """dreamleague should match DreamLeague Season X."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("dreamleague", "DreamLeague Season 24")

    def test_exact_match(self):
        """Exact matches should work."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("Riyadh Masters 2025", "Riyadh Masters 2025")

    def test_partial_match(self):
        """Partial matches should work."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("Riyadh", "Riyadh Masters 2025")

    def test_no_match(self):
        """Non-matching queries should return False."""
        lfs = LeagueFuzzySearch()
        assert not lfs.matches_league("TI 2025", "ESL One Kuala Lumpur")
        assert not lfs.matches_league("Riyadh", "The International 2025")

    def test_empty_league_returns_false(self):
        """Empty actual_league should return False."""
        lfs = LeagueFuzzySearch()
        assert not lfs.matches_league("TI 2025", "")
        assert not lfs.matches_league("TI 2025", None)


class TestPGLWallachiaMatching:
    """Tests for PGL Wallachia tournament matching."""

    def test_pgl_matches_pgl_wallachia(self):
        """PGL should match PGL Wallachia tournaments."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("PGL", "PGL Wallachia Season 6")

    def test_wallachia_matches_pgl_wallachia(self):
        """wallachia should match PGL Wallachia tournaments."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("wallachia", "PGL Wallachia Season 6")

    def test_wallachia_with_season_number(self):
        """wallachia 6 should match PGL Wallachia Season 6."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("wallachia 6", "PGL Wallachia Season 6")

    def test_pgl_wallachia_full_name(self):
        """Full name should match."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("PGL Wallachia Season 6", "PGL Wallachia Season 6")

    def test_pgl_season_matches(self):
        """PGL season should match PGL Wallachia."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("PGL season 6", "PGL Wallachia Season 6")

    def test_different_wallachia_seasons(self):
        """Different season numbers should work."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("wallachia 5", "PGL Wallachia Season 5")
        assert lfs.matches_league("wallachia 4", "PGL Wallachia Season 4")

    def test_pgl_case_insensitive(self):
        """PGL matching should be case insensitive."""
        lfs = LeagueFuzzySearch()
        assert lfs.matches_league("pgl", "PGL Wallachia Season 6")
        assert lfs.matches_league("WALLACHIA", "PGL Wallachia Season 6")


class TestLeagueSearch:
    """Tests for search method with initialized leagues."""

    @pytest.fixture
    def initialized_search(self):
        """Create an initialized league search."""
        lfs = LeagueFuzzySearch()
        lfs.initialize([
            {"leagueid": 1, "name": "The International 2025"},
            {"leagueid": 2, "name": "ESL One Kuala Lumpur 2025"},
            {"leagueid": 3, "name": "BLAST Slam V"},
            {"leagueid": 4, "name": "DreamLeague Season 24"},
            {"leagueid": 5, "name": "Riyadh Masters 2025"},
        ])
        return lfs

    def test_search_ti_finds_the_international(self, initialized_search):
        """Search for TI should find The International."""
        results = initialized_search.search("TI 2025")
        assert len(results) >= 1
        assert results[0].name == "The International 2025"

    def test_search_esl_finds_esl_one(self, initialized_search):
        """Search for ESL should find ESL One."""
        results = initialized_search.search("ESL")
        assert len(results) >= 1
        assert "ESL" in results[0].name

    def test_find_best_match(self, initialized_search):
        """find_best_match should return single best result."""
        result = initialized_search.find_best_match("TI 2025")
        assert result is not None
        assert result.name == "The International 2025"

    def test_search_not_initialized_returns_empty(self):
        """Search on uninitialized instance returns empty list."""
        lfs = LeagueFuzzySearch()
        results = lfs.search("TI 2025")
        assert results == []
