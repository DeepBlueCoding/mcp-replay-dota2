"""
Sampling utilities for coaching analysis.

Uses MCP sampling to request LLM interpretation of Dota 2 data.
If sampling is not supported by the client, returns None.
"""

import logging
from typing import Optional

from fastmcp import Context

logger = logging.getLogger(__name__)


async def try_coaching_analysis(
    ctx: Optional[Context],
    prompt: str,
    max_tokens: int = 600,
) -> Optional[str]:
    """
    Try to get coaching analysis via MCP sampling.

    Args:
        ctx: FastMCP context (may be None if not provided)
        prompt: The coaching prompt to send
        max_tokens: Maximum tokens for the response

    Returns:
        Coaching analysis string if sampling succeeded, None otherwise.
        Returns None if:
        - ctx is None
        - Client doesn't support sampling
        - Sampling request fails for any reason
    """
    if ctx is None:
        logger.debug("No context provided, skipping sampling")
        return None

    try:
        response = await ctx.sample(prompt, max_tokens=max_tokens)
        if response and hasattr(response, "text"):
            return response.text
        return None
    except NotImplementedError:
        logger.debug("Client does not support sampling")
        return None
    except AttributeError:
        logger.debug("Context does not have sample method")
        return None
    except Exception as e:
        logger.warning(f"Sampling failed: {e}")
        return None


async def try_coaching_analysis_with_system(
    ctx: Optional[Context],
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 600,
) -> Optional[str]:
    """
    Try to get coaching analysis with a system prompt.

    Some sampling implementations support system prompts for better control.
    Falls back to combining prompts if system prompt not supported.

    Args:
        ctx: FastMCP context
        system_prompt: System-level instructions
        user_prompt: User-level query/data
        max_tokens: Maximum tokens for the response

    Returns:
        Coaching analysis string if sampling succeeded, None otherwise.
    """
    if ctx is None:
        return None

    combined_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        response = await ctx.sample(combined_prompt, max_tokens=max_tokens)
        if response and hasattr(response, "text"):
            return response.text
        return None
    except Exception as e:
        logger.warning(f"Sampling with system prompt failed: {e}")
        return None
