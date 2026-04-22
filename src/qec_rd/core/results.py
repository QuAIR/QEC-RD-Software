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
    metadata: dict[str, Any] = field(default_factory=dict)
