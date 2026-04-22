from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.core.codes import CodeSpec
from qec_rd.core.types import CircuitSourceKind


@dataclass(frozen=True, slots=True)
class CircuitArtifact:
    source_kind: CircuitSourceKind
    source_format: str
    code_spec: CodeSpec | None = None
    origin_metadata: dict[str, Any] = field(default_factory=dict)
    raw_handle: Any | None = None


@dataclass(frozen=True, slots=True)
class DemArtifact:
    num_detectors: int
    num_observables: int
    dem_text: str
    origin_metadata: dict[str, Any] = field(default_factory=dict)
    raw_handle: Any | None = None


@dataclass(frozen=True, slots=True)
class DecodingGraph:
    num_detectors: int
    num_observables: int
    check_matrix: csc_matrix
    observable_matrix: np.ndarray
    error_probabilities: np.ndarray
    edge_fault_ids: list[int]
    raw_dem_handle: Any | None = None
