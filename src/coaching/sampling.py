"""
Sampling utilities for coaching analysis.

Uses MCP sampling to request LLM interpretation of Dota 2 data.
If sampling is not supported by the client, returns None.
"""

import logging
from typing import Optional

from fastmcp import Context

logger = logging.getLogger(__name__)

# Track sampling support status to avoid repeated log messages
_sampling_support_checked = False
_sampling_supported = False


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
    global _sampling_support_checked, _sampling_supported

    if ctx is None:
        logger.debug("[Sampling] No context provided, skipping sampling")
        return None

    prompt_preview = prompt[:100].replace("\n", " ") + "..." if len(prompt) > 100 else prompt
    logger.debug(f"[Sampling] Attempting sampling request (max_tokens={max_tokens})")
    logger.debug(f"[Sampling] Prompt preview: {prompt_preview}")

    try:
        response = await ctx.sample(prompt, max_tokens=max_tokens)

        if not _sampling_support_checked:
            _sampling_support_checked = True
            _sampling_supported = True
            logger.info("[Sampling] MCP client supports sampling - coaching analysis enabled")

        if response and hasattr(response, "text"):
            response_len = len(response.text) if response.text else 0
            logger.debug(f"[Sampling] Success - received {response_len} chars")
            return response.text

        logger.debug("[Sampling] Response received but no text content")
        return None

    except NotImplementedError:
        if not _sampling_support_checked:
            _sampling_support_checked = True
            _sampling_supported = False
            logger.info("[Sampling] MCP client does NOT support sampling - coaching analysis disabled")
        else:
            logger.debug("[Sampling] Skipped - client does not support sampling")
        return None

    except AttributeError as e:
        if not _sampling_support_checked:
            _sampling_support_checked = True
            _sampling_supported = False
            logger.info(f"[Sampling] Context missing sample method - coaching analysis disabled: {e}")
        return None

    except Exception as e:
        logger.warning(f"[Sampling] Request failed with error: {type(e).__name__}: {e}")
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
    global _sampling_support_checked, _sampling_supported

    if ctx is None:
        logger.debug("[Sampling] No context provided, skipping sampling with system prompt")
        return None

    if _sampling_support_checked and not _sampling_supported:
        logger.debug("[Sampling] Skipped - client does not support sampling")
        return None

    combined_prompt = f"{system_prompt}\n\n{user_prompt}"
    logger.debug(f"[Sampling] Attempting sampling with system prompt (max_tokens={max_tokens})")

    try:
        response = await ctx.sample(combined_prompt, max_tokens=max_tokens)

        if not _sampling_support_checked:
            _sampling_support_checked = True
            _sampling_supported = True
            logger.info("[Sampling] MCP client supports sampling - coaching analysis enabled")

        if response and hasattr(response, "text"):
            response_len = len(response.text) if response.text else 0
            logger.debug(f"[Sampling] Success - received {response_len} chars")
            return response.text

        logger.debug("[Sampling] Response received but no text content")
        return None

    except NotImplementedError:
        if not _sampling_support_checked:
            _sampling_support_checked = True
            _sampling_supported = False
            logger.info("[Sampling] MCP client does NOT support sampling - coaching analysis disabled")
        return None

    except Exception as e:
        logger.warning(f"[Sampling] Request with system prompt failed: {type(e).__name__}: {e}")
        return None


def is_sampling_supported() -> bool:
    """Check if sampling has been determined to be supported by the client."""
    return _sampling_supported


def reset_sampling_status() -> None:
    """Reset sampling support status (useful for testing)."""
    global _sampling_support_checked, _sampling_supported
    _sampling_support_checked = False
    _sampling_supported = False
