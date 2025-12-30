"""
Persona loader for coaching analysis.

Loads analysis personas and frameworks from data/personas/ directory.
"""

from functools import lru_cache
from pathlib import Path

PERSONAS_DIR = Path(__file__).parent.parent.parent / "data" / "personas"


@lru_cache(maxsize=10)
def load_persona(name: str) -> str:
    """
    Load a persona file by name.

    Args:
        name: Persona name without extension (e.g., "coaching_persona", "pos1_carry")

    Returns:
        Content of the persona file.

    Raises:
        FileNotFoundError: If persona file doesn't exist.
    """
    filepath = PERSONAS_DIR / f"{name}.md"
    return filepath.read_text()


def get_coaching_persona() -> str:
    """Load the main coaching persona."""
    return load_persona("coaching_persona")


def get_position_framework(position: int) -> str | None:
    """
    Load position-specific analysis framework if available.

    Args:
        position: Position number (1-5)

    Returns:
        Framework content or None if not available.
    """
    position_files = {
        1: "pos1_carry",
        2: "pos2_mid",
        3: "pos3_offlane",
        4: "pos4_soft_support",
        5: "pos5_hard_support",
    }

    filename = position_files.get(position)
    if not filename:
        return None

    try:
        return load_persona(filename)
    except FileNotFoundError:
        return None
