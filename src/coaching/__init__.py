"""Coaching module for Dota 2 analysis with LLM sampling."""

from .prompts import (
    get_death_analysis_prompt,
    get_hero_performance_prompt,
    get_lane_analysis_prompt,
    get_teamfight_analysis_prompt,
)
from .sampling import try_coaching_analysis

__all__ = [
    "get_hero_performance_prompt",
    "get_death_analysis_prompt",
    "get_lane_analysis_prompt",
    "get_teamfight_analysis_prompt",
    "try_coaching_analysis",
]
