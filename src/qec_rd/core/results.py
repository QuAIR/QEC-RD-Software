from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class SyndromeBatch:
    detection_events: np.ndarray
    observable_flips: np.ndarray | None
    measurements: np.ndarray | None
    shot_count: int
    seed: int | None
    source: str


@dataclass(frozen=True, slots=True)
class DecodeResult:
    decoder_name: str
    predicted_observables: np.ndarray
    actual_observables: np.ndarray | None
    corrections: np.ndarray | None
    failure_mask: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def failure_count(self) -> int:
        return int(self.failure_mask.sum())


@dataclass(frozen=True, slots=True)
class AnalysisReport:
    decoder_name: str
    shot_count: int
    failure_count: int
    logical_error_rate: float
    logical_error_rate_stderr: float
    logical_failure_counts: np.ndarray = field(
        default_factory=lambda: np.zeros(0, dtype=np.int64)
    )
    logical_failure_rates: np.ndarray = field(
        default_factory=lambda: np.zeros(0, dtype=np.float64)
    )
    logical_error_distribution: dict[tuple[bool, ...], int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
