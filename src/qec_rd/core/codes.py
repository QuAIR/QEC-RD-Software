from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_STAGE1_BUILTIN_FAMILIES = frozenset(
    {
        "repetition_code:memory",
        "rotated_surface_code",
        "unrotated_surface_code",
        "toric_code",
    }
)


@dataclass(frozen=True, slots=True)
class CodeSpec:
    family: str
    distance: int
    rounds: int
    logical_basis: str = "Z"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.distance <= 0:
            raise ValueError("distance must be greater than zero")
        if self.rounds <= 0:
            raise ValueError("rounds must be greater than zero")
        if self.family not in SUPPORTED_STAGE1_BUILTIN_FAMILIES:
            raise ValueError(f"unsupported built-in family: {self.family}")
