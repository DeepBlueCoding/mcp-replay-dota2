"""Custom Pydantic types for automatic type coercion."""

from typing import Annotated, List

from pydantic import BeforeValidator


def _coerce_to_int(v):
    """Convert float to int, handling None."""
    if v is None:
        return v
    return int(v)


def _coerce_list_to_int(v):
    """Convert list of floats to list of ints."""
    if v is None:
        return v
    return [int(x) for x in v]


CoercedInt = Annotated[int, BeforeValidator(_coerce_to_int)]
CoercedIntList = Annotated[List[int], BeforeValidator(_coerce_list_to_int)]
