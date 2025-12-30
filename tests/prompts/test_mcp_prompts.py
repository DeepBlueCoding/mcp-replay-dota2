"""Tests for MCP prompts.

Prompts are templates that guide LLM analysis. Each prompt should:
1. Return a string (not a Prompt object)
2. Focus on its specific domain (draft, performance, deaths, etc.)
3. NOT include analysis from other domains
"""

from unittest.mock import MagicMock

import pytest


class TestAnalyzeDraftPrompt:
    """Tests for analyze_draft prompt - should focus ONLY on draft analysis."""

    @pytest.fixture
    def mcp_mock(self):
        """Create mock MCP server to capture registered prompts."""
        mcp = MagicMock()
        prompts = {}

        def prompt_decorator(func):
            prompts[func.__name__] = func
            return func

        mcp.prompt = prompt_decorator
        mcp._prompts = prompts
        return mcp

    @pytest.fixture
    def analyze_draft_func(self, mcp_mock):
        """Get the analyze_draft function after registration."""
        from src.prompts.mcp_prompts import register_prompts
        register_prompts(mcp_mock)
        return mcp_mock._prompts["analyze_draft"]

    def test_returns_string(self, analyze_draft_func):
        """Prompt should return a string, not a Prompt object."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend, Earthshaker, Shadow Demon, Pugna",
            dire_picks="Medusa, Pangolier, Magnus, Naga Siren, Disruptor",
        )
        assert isinstance(result, str)

    def test_includes_lane_matchups_section(self, analyze_draft_func):
        """Draft analysis should include lane matchups."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        assert "Lane Matchups" in result

    def test_includes_synergies_section(self, analyze_draft_func):
        """Draft analysis should include synergies."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        assert "Synergies" in result

    def test_includes_counter_picks_section(self, analyze_draft_func):
        """Draft analysis should include counter picks."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        assert "Counter Picks" in result

    def test_includes_draft_weaknesses_section(self, analyze_draft_func):
        """Draft analysis should include draft weaknesses."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        assert "Weaknesses" in result

    def test_includes_draft_grade_section(self, analyze_draft_func):
        """Draft analysis should include draft grade."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        assert "Draft Grade" in result

    def test_excludes_teamfight_analysis(self, analyze_draft_func):
        """Draft prompt should NOT include teamfight combo analysis."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        # Draft analysis focuses on laning/counters/itemization, not teamfight combos
        assert "teamfight combo" not in result.lower()

    def test_includes_itemization_implications(self, analyze_draft_func):
        """Draft prompt should include itemization implications."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        # Should include itemization analysis section
        assert "Itemization" in result or "item" in result.lower()

    def test_includes_bans_when_provided(self, analyze_draft_func):
        """Draft analysis should include bans section when provided."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
            radiant_bans="Chen, Sand King",
            dire_bans="Bane, Centaur",
        )
        assert "Bans" in result
        assert "Chen, Sand King" in result
        assert "Bane, Centaur" in result

    def test_no_bans_section_when_not_provided(self, analyze_draft_func):
        """Draft analysis should not have bans in content when not provided."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend",
            dire_picks="Medusa, Pangolier",
        )
        # Bans section header should not appear if no bans
        lines = result.split("\n")
        bans_header_lines = [line for line in lines if line.strip() == "## Bans"]
        assert len(bans_header_lines) == 0

    def test_includes_picks_in_output(self, analyze_draft_func):
        """Draft analysis should include the picks provided."""
        result = analyze_draft_func(
            radiant_picks="Juggernaut, Shadow Fiend, Earthshaker",
            dire_picks="Medusa, Pangolier, Magnus",
        )
        assert "Juggernaut, Shadow Fiend, Earthshaker" in result
        assert "Medusa, Pangolier, Magnus" in result


class TestReviewHeroPerformancePrompt:
    """Tests for review_hero_performance prompt."""

    @pytest.fixture
    def mcp_mock(self):
        """Create mock MCP server."""
        mcp = MagicMock()
        prompts = {}

        def prompt_decorator(func):
            prompts[func.__name__] = func
            return func

        mcp.prompt = prompt_decorator
        mcp._prompts = prompts
        return mcp

    @pytest.fixture
    def review_performance_func(self, mcp_mock):
        """Get the review_hero_performance function."""
        from src.prompts.mcp_prompts import register_prompts
        register_prompts(mcp_mock)
        return mcp_mock._prompts["review_hero_performance"]

    def test_returns_string(self, review_performance_func):
        """Prompt should return a string."""
        result = review_performance_func(
            hero="Juggernaut",
            position="1",
            kda="8/2/5",
        )
        assert isinstance(result, str)

    def test_includes_position(self, review_performance_func):
        """Should include position in prompt."""
        result = review_performance_func(
            hero="Juggernaut",
            position="1",
            kda="8/2/5",
        )
        assert "Position 1" in result

    def test_includes_coaching_sections(self, review_performance_func):
        """Should include coaching-specific sections."""
        result = review_performance_func(
            hero="Juggernaut",
            position="1",
            kda="8/2/5",
        )
        assert "Rating" in result
        assert "Issues" in result or "Improvements" in result


class TestAnalyzeDeathsPrompt:
    """Tests for analyze_deaths prompt."""

    @pytest.fixture
    def mcp_mock(self):
        """Create mock MCP server."""
        mcp = MagicMock()
        prompts = {}

        def prompt_decorator(func):
            prompts[func.__name__] = func
            return func

        mcp.prompt = prompt_decorator
        mcp._prompts = prompts
        return mcp

    @pytest.fixture
    def analyze_deaths_func(self, mcp_mock):
        """Get the analyze_deaths function."""
        from src.prompts.mcp_prompts import register_prompts
        register_prompts(mcp_mock)
        return mcp_mock._prompts["analyze_deaths"]

    def test_returns_string(self, analyze_deaths_func):
        """Prompt should return a string."""
        result = analyze_deaths_func(
            deaths_list="4:48 - Earthshaker killed by Disruptor",
        )
        assert isinstance(result, str)

    def test_includes_death_analysis_points(self, analyze_deaths_func):
        """Should include key death analysis points."""
        result = analyze_deaths_func(
            deaths_list="4:48 - Earthshaker killed by Disruptor",
        )
        # Simplified prompt includes inline hints about what to consider
        assert "vision" in result.lower() or "buyback" in result.lower()
        assert "Categories" in result or "Patterns" in result


class TestAnalyzeTeamfightPrompt:
    """Tests for analyze_teamfight prompt."""

    @pytest.fixture
    def mcp_mock(self):
        """Create mock MCP server."""
        mcp = MagicMock()
        prompts = {}

        def prompt_decorator(func):
            prompts[func.__name__] = func
            return func

        mcp.prompt = prompt_decorator
        mcp._prompts = prompts
        return mcp

    @pytest.fixture
    def analyze_teamfight_func(self, mcp_mock):
        """Get the analyze_teamfight function."""
        from src.prompts.mcp_prompts import register_prompts
        register_prompts(mcp_mock)
        return mcp_mock._prompts["analyze_teamfight"]

    def test_returns_string(self, analyze_teamfight_func):
        """Prompt should return a string."""
        result = analyze_teamfight_func(
            fight_time="25:30",
            participants="Earthshaker, Medusa, Magnus",
            death_sequence="25:32 - Earthshaker dies",
        )
        assert isinstance(result, str)

    def test_includes_teamfight_sections(self, analyze_teamfight_func):
        """Should include teamfight-specific analysis sections."""
        result = analyze_teamfight_func(
            fight_time="25:30",
            participants="Earthshaker, Medusa, Magnus",
            death_sequence="25:32 - Earthshaker dies",
        )
        assert "Initiation" in result
        assert "Target Priority" in result or "Positioning" in result


class TestPromptRegistration:
    """Tests for prompt registration with MCP server."""

    def test_all_prompts_registered(self):
        """All expected prompts should be registered."""
        mcp = MagicMock()
        prompts = {}

        def prompt_decorator(func):
            prompts[func.__name__] = func
            return func

        mcp.prompt = prompt_decorator

        from src.prompts.mcp_prompts import register_prompts
        register_prompts(mcp)

        expected_prompts = [
            "analyze_draft",
            "review_hero_performance",
            "analyze_deaths",
            "review_laning_phase",
            "analyze_teamfight",
            "compare_itemization",
            "game_turning_points",
        ]

        for prompt_name in expected_prompts:
            assert prompt_name in prompts, f"Missing prompt: {prompt_name}"

    def test_prompts_are_callable(self):
        """All registered prompts should be callable functions."""
        mcp = MagicMock()
        prompts = {}

        def prompt_decorator(func):
            prompts[func.__name__] = func
            return func

        mcp.prompt = prompt_decorator

        from src.prompts.mcp_prompts import register_prompts
        register_prompts(mcp)

        for name, func in prompts.items():
            assert callable(func), f"Prompt {name} is not callable"
