"""Coaching module for Dota 2 analysis with LLM sampling."""

from .personas import get_coaching_persona, get_position_framework
from .prompts import (
    get_death_analysis_prompt,
    get_hero_performance_prompt,
    get_lane_analysis_prompt,
    get_teamfight_analysis_prompt,
)
from .sampling import is_sampling_supported, reset_sampling_status, try_coaching_analysis

__all__ = [
    "get_coaching_persona",
    "get_position_framework",
    "get_hero_performance_prompt",
    "get_death_analysis_prompt",
    "get_lane_analysis_prompt",
    "get_teamfight_analysis_prompt",
    "try_coaching_analysis",
    "is_sampling_supported",
    "reset_sampling_status",
]
