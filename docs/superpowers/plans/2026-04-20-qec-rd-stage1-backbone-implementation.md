# QEC-RD Stage 1 Backbone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first-stage `qec_rd` platform backbone on top of `stim`, with unified core objects, generated/imported circuit entry points, built-in rotated/unrotated surface and toric code support, simple CSS-code-driven stabilizer measurement circuit generation, fixed DEM-to-graph conversion, Stim sampling, MWPM decoding through `pymatching`, BP+OSD decoding through `ldpc`, custom decoder integration hooks, and basic analysis.

**Architecture:** Keep `stim` as the only runtime backend and implement the platform logic inside `qec_rd`. The package structure follows the approved backbone design: `core` for stable objects, `adapters.stim` for backend conversion, `kernel.*` for circuit/graph/decode/analysis logic, and `api` as a thin public surface. The implementation should first stabilize the object model and code/circuit entry, then add built-in surface/toric and CSS-driven circuit generation, then open the fixed DEM/graph chain, then add MWPM and BP+OSD decoding plus custom-decoder hooks, and finally close the loop with analysis and integration tests.

**Tech Stack:** Python 3.10+, `stim`, `numpy`, `scipy`, `pytest`, `pymatching`, `ldpc`

---

## File Structure

### New source files

- `src/qec_rd/api.py`
  Thin public API functions for circuit building/loading, DEM extraction, graph construction, sampling, decoding, and analysis.
- `src/qec_rd/core/__init__.py`
  Re-exports the core platform objects.
- `src/qec_rd/core/codes.py`
  Defines `CodeSpec` and code-description structures for built-in and CSS-driven circuit generation.
- `src/qec_rd/core/noise.py`
  Defines a Stim-compatible Pauli-noise `NoiseModel`.
- `src/qec_rd/core/artifacts.py`
  Defines `CircuitArtifact`, `DemArtifact`, `DecodingGraph`, and graph-supporting data containers.
- `src/qec_rd/core/results.py`
  Defines `SyndromeBatch`, `DecodeResult`, and `AnalysisReport`.
- `src/qec_rd/core/types.py`
  Shared enums, type aliases, and platform exception types.
- `src/qec_rd/adapters/__init__.py`
  Package marker for adapters.
- `src/qec_rd/adapters/stim.py`
  Bridges between `stim` and the platform object model.
- `src/qec_rd/kernel/__init__.py`
  Package marker for kernel modules.
- `src/qec_rd/kernel/circuit.py`
  Generated/imported circuit entry logic, including built-in surface/toric support and CSS-driven stabilizer measurement circuits.
- `src/qec_rd/kernel/graph.py`
  DEM extraction and decoding graph construction.
- `src/qec_rd/kernel/decode.py`
  External decoder adaptation for MWPM, BP+OSD, and custom decoders.
- `src/qec_rd/kernel/analysis.py`
  Basic logical error rate and batch analysis.

### Modified source files

- `pyproject.toml`
  Add Stage 1 runtime/test dependencies.
- `src/qec_rd/__init__.py`
  Keep package version metadata stable during the scaffold step.

### New test files

- `tests/test_backbone_imports.py`
  Package layout and import smoke tests.
- `tests/test_core_models.py`
  Core object model tests.
- `tests/test_circuit_entry.py`
  Generated and imported circuit entry tests.
- `tests/test_builtin_codes.py`
  Built-in rotated/unrotated surface and toric code circuit tests.
- `tests/test_css_codegen.py`
  User-defined CSS-code circuit generation tests.
- `tests/test_dem_graph.py`
  DEM extraction and graph construction tests.
- `tests/test_sampling.py`
  Stim sampling to `SyndromeBatch` tests.
- `tests/test_decode_pymatching.py`
  MWPM adapter tests.
- `tests/test_decode_bposd.py`
  BP+OSD adapter tests.
- `tests/test_decode_custom.py`
  Custom decoder end-to-end tests.
- `tests/test_analysis.py`
  Analysis object and logical error rate tests.
- `tests/integration/test_generated_pipeline.py`
  Generated-circuit end-to-end pipeline test.
- `tests/integration/test_imported_pipeline.py`
  Imported-circuit end-to-end pipeline test.

---

### Task 1: Package Scaffold and Dependencies

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/qec_rd/__init__.py`
- Create: `src/qec_rd/api.py`
- Create: `src/qec_rd/core/__init__.py`
- Create: `src/qec_rd/adapters/__init__.py`
- Create: `src/qec_rd/kernel/__init__.py`
- Test: `tests/test_backbone_imports.py`

- [ ] **Step 1: Write the failing import smoke test**

```python
# tests/test_backbone_imports.py
from importlib import import_module


def test_stage1_modules_are_importable():
    modules = [
        "qec_rd.api",
        "qec_rd.core",
        "qec_rd.adapters.stim",
        "qec_rd.kernel.circuit",
        "qec_rd.kernel.graph",
        "qec_rd.kernel.decode",
        "qec_rd.kernel.analysis",
    ]
    for module_name in modules:
        import_module(module_name)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_backbone_imports.py -v`

Expected: FAIL with one or more `ModuleNotFoundError` errors for the missing Stage 1 modules.

- [ ] **Step 3: Add dependencies and package skeleton files**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "qec-rd-software"
version = "0.1.0"
description = "QEC R&D software backbone built on Stim with extensible circuit, graph, decode, and analysis layers."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "Apache-2.0" }
dependencies = [
    "numpy>=1.26",
    "scipy>=1.13",
    "stim>=1.14,<2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pymatching>=2.2",
    "ldpc>=2.3",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# src/qec_rd/__init__.py
"""QEC-RD platform package."""

__version__ = "0.1.0"
```

```python
# src/qec_rd/api.py
"""Thin Stage 1 public API."""
```

```python
# src/qec_rd/core/__init__.py
"""Core platform object model."""
```

```python
# src/qec_rd/adapters/__init__.py
"""Backend adapters."""
```

```python
# src/qec_rd/kernel/__init__.py
"""Platform kernel modules."""
```

```python
# src/qec_rd/adapters/stim.py
"""Stim adapter module."""
```

```python
# src/qec_rd/kernel/circuit.py
"""Circuit entry logic."""
```

```python
# src/qec_rd/kernel/graph.py
"""DEM and graph logic."""
```

```python
# src/qec_rd/kernel/decode.py
"""Decoder adaptation logic."""
```

```python
# src/qec_rd/kernel/analysis.py
"""Analysis logic."""
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_backbone_imports.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/qec_rd/__init__.py src/qec_rd/api.py src/qec_rd/core/__init__.py src/qec_rd/adapters/__init__.py src/qec_rd/adapters/stim.py src/qec_rd/kernel/__init__.py src/qec_rd/kernel/circuit.py src/qec_rd/kernel/graph.py src/qec_rd/kernel/decode.py src/qec_rd/kernel/analysis.py tests/test_backbone_imports.py
git commit -m "build: scaffold stage1 backbone modules"
```

---

### Task 2: Core Object Model

**Files:**
- Create: `src/qec_rd/core/types.py`
- Create: `src/qec_rd/core/codes.py`
- Create: `src/qec_rd/core/noise.py`
- Create: `src/qec_rd/core/artifacts.py`
- Create: `src/qec_rd/core/results.py`
- Modify: `src/qec_rd/core/__init__.py`
- Test: `tests/test_core_models.py`

- [ ] **Step 1: Write the failing core model tests**

```python
# tests/test_core_models.py
import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.core import (
    AnalysisReport,
    CircuitArtifact,
    CircuitSourceKind,
    CodeSpec,
    DecodeResult,
    DecodingGraph,
    NoiseModel,
    SyndromeBatch,
)


def test_core_objects_capture_stage1_metadata():
    code = CodeSpec(family="repetition_code:memory", distance=3, rounds=3)
    noise = NoiseModel(after_clifford_depolarization=1e-3)
    circuit = CircuitArtifact(
        source_kind=CircuitSourceKind.GENERATED,
        source_format="stim",
        code_spec=code,
        origin_metadata={"generator": "stim.generated"},
    )

    graph = DecodingGraph(
        num_detectors=3,
        num_observables=1,
        check_matrix=csc_matrix([[1, 0], [0, 1], [1, 1]], dtype=np.uint8),
        observable_matrix=np.array([[1, 0]], dtype=np.uint8),
        error_probabilities=np.array([0.1, 0.2]),
        edge_fault_ids=[0, 1],
        raw_dem_handle=None,
    )

    batch = SyndromeBatch(
        detection_events=np.zeros((4, 3), dtype=np.bool_),
        observable_flips=np.zeros((4, 1), dtype=np.bool_),
        measurements=None,
        shot_count=4,
        seed=5,
        source="stim.detector_sampler",
    )

    result = DecodeResult(
        decoder_name="pymatching",
        predicted_observables=np.zeros((4, 1), dtype=np.bool_),
        actual_observables=np.zeros((4, 1), dtype=np.bool_),
        corrections=np.zeros((4, 2), dtype=np.uint8),
        failure_mask=np.zeros(4, dtype=np.bool_),
        metadata={"distance": 3},
    )

    report = AnalysisReport(
        decoder_name="pymatching",
        shot_count=4,
        failure_count=0,
        logical_error_rate=0.0,
        logical_error_rate_stderr=0.0,
        metadata={"kind": "unit"},
    )

    assert circuit.code_spec == code
    assert noise.after_clifford_depolarization == 1e-3
    assert graph.check_matrix.shape == (3, 2)
    assert batch.shot_count == 4
    assert result.failure_count == 0
    assert report.logical_error_rate == 0.0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_core_models.py -v`

Expected: FAIL with `ImportError` or `AttributeError` because the core types do not exist yet.

- [ ] **Step 3: Implement the core model layer**

```python
# src/qec_rd/core/types.py
from __future__ import annotations

from enum import Enum


class QecRdError(Exception):
    """Base exception for platform-level errors."""


class UnsupportedCircuitFormatError(QecRdError):
    """Raised when a circuit format is not supported."""


class UnsupportedDemError(QecRdError):
    """Raised when a DEM cannot be converted into the Stage 1 graph model."""


class DecoderConfigurationError(QecRdError):
    """Raised when decoder inputs or options are invalid."""


class CircuitSourceKind(str, Enum):
    GENERATED = "generated"
    STIM_OBJECT = "stim_object"
    STIM_FILE = "stim_file"
    QASM_FILE = "qasm_file"
```

```python
# src/qec_rd/core/codes.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CodeSpec:
    family: str
    distance: int
    rounds: int
    logical_basis: str = "Z"
    metadata: dict[str, Any] = field(default_factory=dict)
```

```python
# src/qec_rd/core/noise.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NoiseModel:
    # Stage 1 keeps noise limited to Stim-executable Pauli-like parameters.
    after_clifford_depolarization: float | None = None
    before_round_data_depolarization: float | None = None
    before_measure_flip_probability: float | None = None
    after_reset_flip_probability: float | None = None
```

```python
# src/qec_rd/core/artifacts.py
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
```

```python
# src/qec_rd/core/results.py
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
```

```python
# src/qec_rd/core/__init__.py
from qec_rd.core.artifacts import CircuitArtifact, DecodingGraph, DemArtifact
from qec_rd.core.codes import CodeSpec
from qec_rd.core.noise import NoiseModel
from qec_rd.core.results import AnalysisReport, DecodeResult, SyndromeBatch
from qec_rd.core.types import (
    CircuitSourceKind,
    DecoderConfigurationError,
    QecRdError,
    UnsupportedCircuitFormatError,
    UnsupportedDemError,
)

__all__ = [
    "AnalysisReport",
    "CircuitArtifact",
    "CircuitSourceKind",
    "CodeSpec",
    "DecodeResult",
    "DecodingGraph",
    "DecoderConfigurationError",
    "DemArtifact",
    "NoiseModel",
    "QecRdError",
    "SyndromeBatch",
    "UnsupportedCircuitFormatError",
    "UnsupportedDemError",
]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_core_models.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/core/__init__.py src/qec_rd/core/types.py src/qec_rd/core/codes.py src/qec_rd/core/noise.py src/qec_rd/core/artifacts.py src/qec_rd/core/results.py tests/test_core_models.py
git commit -m "feat(core): add stage1 object model"
```

---

### Task 2A: Built-In Code Families and CSS CodeSpec Shapes

**Files:**
- Modify: `src/qec_rd/core/codes.py`
- Modify: `src/qec_rd/core/__init__.py`
- Test: `tests/test_builtin_codes.py`
- Test: `tests/test_css_codegen.py`

- [ ] **Step 1: Write the failing built-in-code and CSS-shape tests**

```python
# tests/test_builtin_codes.py
from qec_rd.core import CodeSpec


def test_codespec_supports_stage1_builtin_code_families():
    rotated = CodeSpec(family="rotated_surface_code", distance=3, rounds=3)
    unrotated = CodeSpec(family="unrotated_surface_code", distance=3, rounds=3)
    toric = CodeSpec(family="toric_code", distance=4, rounds=4)

    assert rotated.family == "rotated_surface_code"
    assert unrotated.family == "unrotated_surface_code"
    assert toric.family == "toric_code"
```

```python
# tests/test_css_codegen.py
import numpy as np

from qec_rd.core import CodeSpec


def test_codespec_accepts_user_defined_css_code_information():
    hx = np.array([[1, 1, 0, 0], [0, 0, 1, 1]], dtype=np.uint8)
    hz = np.array([[1, 0, 1, 0], [0, 1, 0, 1]], dtype=np.uint8)
    code = CodeSpec(
        family="css_code",
        distance=2,
        rounds=2,
        metadata={"hx": hx, "hz": hz, "name": "toy_css"},
    )

    assert code.family == "css_code"
    assert code.metadata["hx"].shape == (2, 4)
    assert code.metadata["hz"].shape == (2, 4)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_builtin_codes.py tests/test_css_codegen.py -v`

Expected: FAIL because `CodeSpec` is still only being exercised for the repetition-code path and does not yet document Stage 1 built-in families or CSS-oriented metadata expectations.

- [ ] **Step 3: Tighten `CodeSpec` for Stage 1 code coverage**

```python
# src/qec_rd/core/codes.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CodeSpec:
    family: str
    distance: int
    rounds: int
    logical_basis: str = "Z"
    metadata: dict[str, Any] = field(default_factory=dict)
```

```python
# src/qec_rd/core/__init__.py
from qec_rd.core.artifacts import CircuitArtifact, DecodingGraph, DemArtifact
from qec_rd.core.codes import CodeSpec
from qec_rd.core.noise import NoiseModel
from qec_rd.core.results import AnalysisReport, DecodeResult, SyndromeBatch
from qec_rd.core.types import (
    CircuitSourceKind,
    DecoderConfigurationError,
    QecRdError,
    UnsupportedCircuitFormatError,
    UnsupportedDemError,
)

__all__ = [
    "AnalysisReport",
    "CircuitArtifact",
    "CircuitSourceKind",
    "CodeSpec",
    "DecodeResult",
    "DecodingGraph",
    "DecoderConfigurationError",
    "DemArtifact",
    "NoiseModel",
    "QecRdError",
    "SyndromeBatch",
    "UnsupportedCircuitFormatError",
    "UnsupportedDemError",
]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_builtin_codes.py tests/test_css_codegen.py -v`

Expected: PASS with `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/core/codes.py src/qec_rd/core/__init__.py tests/test_builtin_codes.py tests/test_css_codegen.py
git commit -m "test(core): cover stage1 builtin code families and css metadata"
```

---

### Task 3: Generated and Imported Circuit Entry

**Files:**
- Modify: `src/qec_rd/adapters/stim.py`
- Modify: `src/qec_rd/kernel/circuit.py`
- Modify: `src/qec_rd/api.py`
- Test: `tests/test_circuit_entry.py`

- [ ] **Step 1: Write the failing circuit entry tests**

```python
# tests/test_circuit_entry.py
from pathlib import Path

import stim

from qec_rd.api import build_circuit, load_circuit
from qec_rd.core import CircuitSourceKind, CodeSpec, NoiseModel


def test_build_circuit_returns_generated_circuit_artifact():
    artifact = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    assert artifact.source_kind is CircuitSourceKind.GENERATED
    assert artifact.source_format == "stim"
    assert isinstance(artifact.raw_handle, stim.Circuit)


def test_load_circuit_accepts_stim_object_and_file(tmp_path: Path):
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        distance=3,
        rounds=3,
        after_clifford_depolarization=1e-3,
    )
    object_artifact = load_circuit(circuit, format="stim")
    assert object_artifact.source_kind is CircuitSourceKind.STIM_OBJECT

    stim_path = tmp_path / "rep_d3.stim"
    stim_path.write_text(str(circuit), encoding="utf-8")
    file_artifact = load_circuit(stim_path, format="stim")
    assert file_artifact.source_kind is CircuitSourceKind.STIM_FILE
    assert file_artifact.origin_metadata["path"].endswith("rep_d3.stim")


def test_build_circuit_supports_builtin_surface_and_toric_families():
    rotated = build_circuit(CodeSpec(family="rotated_surface_code", distance=3, rounds=3))
    unrotated = build_circuit(CodeSpec(family="unrotated_surface_code", distance=3, rounds=3))
    toric = build_circuit(CodeSpec(family="toric_code", distance=4, rounds=4))

    assert isinstance(rotated.raw_handle, stim.Circuit)
    assert isinstance(unrotated.raw_handle, stim.Circuit)
    assert isinstance(toric.raw_handle, stim.Circuit)


def test_build_circuit_supports_user_defined_css_code():
    code = CodeSpec(
        family="css_code",
        distance=2,
        rounds=2,
        metadata={
            "hx": [[1, 1, 0, 0], [0, 0, 1, 1]],
            "hz": [[1, 0, 1, 0], [0, 1, 0, 1]],
        },
    )
    artifact = build_circuit(code)
    assert isinstance(artifact.raw_handle, stim.Circuit)
    assert "MPP" in str(artifact.raw_handle)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_circuit_entry.py -v`

Expected: FAIL because `build_circuit` and `load_circuit` are not implemented.

- [ ] **Step 3: Implement generated/imported circuit entry**

```python
# src/qec_rd/adapters/stim.py
from __future__ import annotations

from pathlib import Path

import numpy as np
import stim

from qec_rd.core import CircuitArtifact, CircuitSourceKind, CodeSpec, NoiseModel, UnsupportedCircuitFormatError


def _stim_generated_name(family: str) -> str:
    mapping = {
        "repetition_code:memory": "repetition_code:memory",
        "rotated_surface_code": "surface_code:rotated_memory_z",
        "unrotated_surface_code": "surface_code:unrotated_memory_z",
        "toric_code": "surface_code:toric_memory_z",
    }
    if family not in mapping:
        raise UnsupportedCircuitFormatError(f"Unsupported Stage 1 generated family: {family!r}")
    return mapping[family]


def _build_simple_css_measurement_circuit(code_spec: CodeSpec) -> stim.Circuit:
    hx = np.asarray(code_spec.metadata["hx"], dtype=np.uint8)
    hz = np.asarray(code_spec.metadata["hz"], dtype=np.uint8)
    num_qubits = hx.shape[1]
    circuit = stim.Circuit()
    circuit.append("R", range(num_qubits))
    for _ in range(code_spec.rounds):
        for row in hx:
            targets = [index for index, value in enumerate(row) if value]
            if targets:
                circuit.append("MPP", [stim.target_x(index) for index in targets])
                circuit.append("DETECTOR", [stim.target_rec(-1)])
        for row in hz:
            targets = [index for index, value in enumerate(row) if value]
            if targets:
                circuit.append("MPP", [stim.target_z(index) for index in targets])
                circuit.append("DETECTOR", [stim.target_rec(-1)])
        circuit.append("TICK")
    circuit.append("MPP", [stim.target_z(0)])
    circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(-1)], 0)
    return circuit


def build_generated_stim_circuit(code_spec: CodeSpec, noise_model: NoiseModel | None) -> CircuitArtifact:
    if code_spec.family == "css_code":
        circuit = _build_simple_css_measurement_circuit(code_spec)
        return CircuitArtifact(
            source_kind=CircuitSourceKind.GENERATED,
            source_format="stim",
            code_spec=code_spec,
            origin_metadata={"generator": "css_measurement_builder"},
            raw_handle=circuit,
        )

    circuit = stim.Circuit.generated(
        _stim_generated_name(code_spec.family),
        distance=code_spec.distance,
        rounds=code_spec.rounds,
        after_clifford_depolarization=noise_model.after_clifford_depolarization if noise_model else 0.0,
    )
    return CircuitArtifact(
        source_kind=CircuitSourceKind.GENERATED,
        source_format="stim",
        code_spec=code_spec,
        origin_metadata={"generator": "stim.Circuit.generated"},
        raw_handle=circuit,
    )


def load_stim_circuit(source: stim.Circuit | str | Path, format: str) -> CircuitArtifact:
    if format != "stim":
        raise UnsupportedCircuitFormatError(f"Unsupported circuit format: {format!r}")
    if isinstance(source, stim.Circuit):
        return CircuitArtifact(
            source_kind=CircuitSourceKind.STIM_OBJECT,
            source_format="stim",
            origin_metadata={"kind": "object"},
            raw_handle=source,
        )
    path = Path(source)
    circuit = stim.Circuit.from_file(path)
    return CircuitArtifact(
        source_kind=CircuitSourceKind.STIM_FILE,
        source_format="stim",
        origin_metadata={"path": str(path)},
        raw_handle=circuit,
    )
```

```python
# src/qec_rd/kernel/circuit.py
from __future__ import annotations

from pathlib import Path

import stim

from qec_rd.adapters.stim import build_generated_stim_circuit, load_stim_circuit
from qec_rd.core import CircuitArtifact, CodeSpec, NoiseModel


def build_circuit(code_spec: CodeSpec, noise_model: NoiseModel | None = None) -> CircuitArtifact:
    return build_generated_stim_circuit(code_spec, noise_model)


def load_circuit(source: stim.Circuit | str | Path, format: str = "stim") -> CircuitArtifact:
    return load_stim_circuit(source, format=format)
```

```python
# src/qec_rd/api.py
from qec_rd.core import CodeSpec, NoiseModel
from qec_rd.kernel.circuit import build_circuit, load_circuit

__all__ = [
    "build_circuit",
    "load_circuit",
    "CodeSpec",
    "NoiseModel",
]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_circuit_entry.py -v`

Expected: PASS with `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/adapters/stim.py src/qec_rd/kernel/circuit.py src/qec_rd/api.py tests/test_circuit_entry.py
git commit -m "feat(circuit): add generated and imported circuit entry"
```

---

### Task 4: DEM Extraction and Decoding Graph Construction

**Files:**
- Modify: `src/qec_rd/adapters/stim.py`
- Modify: `src/qec_rd/kernel/graph.py`
- Test: `tests/test_dem_graph.py`

This task intentionally fixes the Stage 1 DEM and graph-construction path as platform-owned behavior. It is not a user-customization track in this phase.

- [ ] **Step 1: Write the failing DEM/graph tests**

```python
# tests/test_dem_graph.py
import numpy as np

from qec_rd.api import build_circuit, build_decoding_graph, extract_dem
from qec_rd.core import CodeSpec, NoiseModel


def test_extract_dem_and_build_graph_for_generated_repetition_memory():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)

    assert dem.num_detectors > 0
    assert dem.num_observables >= 1
    assert graph.num_detectors == dem.num_detectors
    assert graph.check_matrix.shape[0] == dem.num_detectors
    assert graph.observable_matrix.shape[0] == dem.num_observables
    assert np.all(graph.error_probabilities > 0.0)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_dem_graph.py -v`

Expected: FAIL because `extract_dem` and `build_decoding_graph` are not implemented.

- [ ] **Step 3: Implement DEM extraction and graph construction**

```python
# src/qec_rd/adapters/stim.py
from __future__ import annotations

from pathlib import Path

import stim

from qec_rd.core import (
    CircuitArtifact,
    CircuitSourceKind,
    CodeSpec,
    DemArtifact,
    NoiseModel,
    UnsupportedCircuitFormatError,
)


def extract_stim_dem(circuit_artifact: CircuitArtifact) -> DemArtifact:
    circuit = circuit_artifact.raw_handle
    dem = circuit.detector_error_model(decompose_errors=True)
    return DemArtifact(
        num_detectors=dem.num_detectors,
        num_observables=dem.num_observables,
        dem_text=str(dem),
        origin_metadata={"source_kind": circuit_artifact.source_kind.value},
        raw_handle=dem,
    )
```

```python
# src/qec_rd/kernel/graph.py
from __future__ import annotations

import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.adapters.stim import extract_stim_dem
from qec_rd.core import CircuitArtifact, DecodingGraph, DemArtifact, UnsupportedDemError


def extract_dem(circuit_artifact: CircuitArtifact) -> DemArtifact:
    return extract_stim_dem(circuit_artifact)


def build_decoding_graph(dem_artifact: DemArtifact) -> DecodingGraph:
    dem = dem_artifact.raw_handle
    row_indices: list[int] = []
    col_indices: list[int] = []
    obs_pairs: list[tuple[int, int]] = []
    data: list[int] = []
    error_probabilities: list[float] = []
    edge_fault_ids: list[int] = []
    column = 0

    for instruction in dem:
        if instruction.type != "error":
            continue
        detectors: list[int] = []
        observables: list[int] = []
        for target in instruction.targets_copy():
            if target.is_relative_detector_id():
                detectors.append(target.val)
            elif target.is_logical_observable_id():
                observables.append(target.val)
        if not detectors:
            continue
        if len(detectors) > 2:
            raise UnsupportedDemError("Stage 1 only supports graphlike DEM terms with up to two detectors.")
        error_probability = float(instruction.args_copy()[0])
        for detector in detectors:
            row_indices.append(detector)
            col_indices.append(column)
            data.append(1)
        for observable in observables:
            obs_pairs.append((observable, column))
        error_probabilities.append(error_probability)
        edge_fault_ids.append(column)
        column += 1

    check_matrix = csc_matrix(
        (data, (row_indices, col_indices)),
        shape=(dem_artifact.num_detectors, column),
        dtype=np.uint8,
    )
    observable_matrix = np.zeros((dem_artifact.num_observables, column), dtype=np.uint8)
    for observable, fault_id in obs_pairs:
        observable_matrix[observable, fault_id] = 1

    return DecodingGraph(
        num_detectors=dem_artifact.num_detectors,
        num_observables=dem_artifact.num_observables,
        check_matrix=check_matrix,
        observable_matrix=observable_matrix,
        error_probabilities=np.asarray(error_probabilities, dtype=float),
        edge_fault_ids=edge_fault_ids,
        raw_dem_handle=dem,
    )
```

```python
# src/qec_rd/api.py
from qec_rd.core import CodeSpec, NoiseModel
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.graph import build_decoding_graph, extract_dem

__all__ = [
    "build_circuit",
    "build_decoding_graph",
    "extract_dem",
    "load_circuit",
    "CodeSpec",
    "NoiseModel",
]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_dem_graph.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/adapters/stim.py src/qec_rd/kernel/graph.py tests/test_dem_graph.py
git commit -m "feat(graph): add dem extraction and graph construction"
```

---

### Task 5: Stim Sampling into `SyndromeBatch`

**Files:**
- Modify: `src/qec_rd/adapters/stim.py`
- Modify: `src/qec_rd/kernel/graph.py`
- Test: `tests/test_sampling.py`

- [ ] **Step 1: Write the failing sampling test**

```python
# tests/test_sampling.py
import numpy as np

from qec_rd.api import build_circuit, sample_syndromes
from qec_rd.core import CodeSpec, NoiseModel


def test_sample_syndromes_returns_standard_batch():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    batch = sample_syndromes(circuit, shots=8, seed=11)

    assert batch.shot_count == 8
    assert batch.detection_events.shape[0] == 8
    assert batch.observable_flips.shape[0] == 8
    assert batch.measurements is None
    assert batch.detection_events.dtype == np.bool_
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_sampling.py -v`

Expected: FAIL because `sample_syndromes` is not implemented.

- [ ] **Step 3: Implement sampling**

```python
# src/qec_rd/adapters/stim.py
from __future__ import annotations

from pathlib import Path

import numpy as np
import stim

from qec_rd.core import (
    CircuitArtifact,
    CircuitSourceKind,
    CodeSpec,
    DemArtifact,
    NoiseModel,
    SyndromeBatch,
    UnsupportedCircuitFormatError,
)


def sample_stim_detectors(
    circuit_artifact: CircuitArtifact,
    *,
    shots: int,
    seed: int | None,
) -> SyndromeBatch:
    sampler = circuit_artifact.raw_handle.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(
        shots=shots,
        separate_observables=True,
    )
    return SyndromeBatch(
        detection_events=np.asarray(detection_events, dtype=np.bool_),
        observable_flips=np.asarray(observable_flips, dtype=np.bool_),
        measurements=None,
        shot_count=shots,
        seed=seed,
        source="stim.detector_sampler",
    )
```

```python
# src/qec_rd/kernel/graph.py
from __future__ import annotations

import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.adapters.stim import extract_stim_dem, sample_stim_detectors
from qec_rd.core import CircuitArtifact, DecodingGraph, DemArtifact, SyndromeBatch, UnsupportedDemError


def sample_syndromes(
    circuit_artifact: CircuitArtifact,
    *,
    shots: int,
    seed: int | None = None,
) -> SyndromeBatch:
    return sample_stim_detectors(circuit_artifact, shots=shots, seed=seed)
```

```python
# src/qec_rd/api.py
from qec_rd.core import CodeSpec, NoiseModel
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes

__all__ = [
    "build_circuit",
    "build_decoding_graph",
    "extract_dem",
    "load_circuit",
    "sample_syndromes",
    "CodeSpec",
    "NoiseModel",
]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_sampling.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/adapters/stim.py src/qec_rd/kernel/graph.py tests/test_sampling.py
git commit -m "feat(sampling): add syndrome batch sampling"
```

---

### Task 6: MWPM Decoder Through `pymatching`

**Files:**
- Modify: `src/qec_rd/kernel/decode.py`
- Modify: `src/qec_rd/api.py`
- Test: `tests/test_decode_pymatching.py`

- [ ] **Step 1: Write the failing MWPM test**

```python
# tests/test_decode_pymatching.py
from qec_rd.api import (
    build_circuit,
    build_decoding_graph,
    extract_dem,
    run_decoder,
    sample_syndromes,
)
from qec_rd.core import CodeSpec, NoiseModel


def test_run_decoder_supports_pymatching():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)
    batch = sample_syndromes(circuit, shots=16, seed=3)
    result = run_decoder(graph, batch, decoder_name="pymatching")

    assert result.decoder_name == "pymatching"
    assert result.predicted_observables.shape == batch.observable_flips.shape
    assert result.failure_mask.shape == (16,)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_decode_pymatching.py -v`

Expected: FAIL because the MWPM decoder adapter is not implemented.

- [ ] **Step 3: Implement the `pymatching` adapter**

```python
# src/qec_rd/kernel/decode.py
from __future__ import annotations

import numpy as np
from pymatching import Matching

from qec_rd.core import DecodeResult, DecoderConfigurationError, DecodingGraph, SyndromeBatch


def normalize_custom_decode_result(
    *,
    decoder_name: str,
    predicted_observables: np.ndarray,
    actual_observables: np.ndarray | None,
    corrections: np.ndarray | None = None,
    metadata: dict | None = None,
) -> DecodeResult:
    if actual_observables is None:
        failure_mask = np.zeros(predicted_observables.shape[0], dtype=np.bool_)
    else:
        failure_mask = np.any(predicted_observables != actual_observables, axis=1)
    return DecodeResult(
        decoder_name=decoder_name,
        predicted_observables=np.asarray(predicted_observables, dtype=np.bool_),
        actual_observables=actual_observables,
        corrections=corrections,
        failure_mask=failure_mask,
        metadata={} if metadata is None else metadata,
    )


def _run_pymatching(graph: DecodingGraph, batch: SyndromeBatch) -> DecodeResult:
    if graph.raw_dem_handle is None:
        raise DecoderConfigurationError("pymatching decoding requires a raw DEM handle.")
    matching = Matching.from_detector_error_model(graph.raw_dem_handle)
    predictions = np.asarray(matching.decode_batch(batch.detection_events), dtype=np.bool_)
    actual = batch.observable_flips
    return normalize_custom_decode_result(
        decoder_name="pymatching",
        predicted_observables=predictions,
        actual_observables=actual,
        corrections=None,
        metadata={"backend": "pymatching"},
    )


def run_decoder(
    graph: DecodingGraph,
    batch: SyndromeBatch,
    *,
    decoder_name: str,
    decoder_fn=None,
    **kwargs,
) -> DecodeResult:
    if decoder_name == "pymatching":
        return _run_pymatching(graph, batch)
    if decoder_name == "custom":
        if decoder_fn is None:
            raise DecoderConfigurationError("Custom decoding requires decoder_fn.")
        result = decoder_fn(graph, batch, **kwargs)
        if not isinstance(result, DecodeResult):
            raise DecoderConfigurationError("Custom decoder must return DecodeResult.")
        return result
    raise DecoderConfigurationError(f"Unsupported decoder: {decoder_name!r}")
```

```python
# src/qec_rd/api.py
from qec_rd.core import CodeSpec, NoiseModel
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.decode import normalize_custom_decode_result, run_decoder
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes

__all__ = [
    "build_circuit",
    "build_decoding_graph",
    "extract_dem",
    "load_circuit",
    "normalize_custom_decode_result",
    "run_decoder",
    "sample_syndromes",
    "CodeSpec",
    "NoiseModel",
]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_decode_pymatching.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/kernel/decode.py src/qec_rd/api.py tests/test_decode_pymatching.py
git commit -m "feat(decode): add pymatching mwpm adapter"
```

---

### Task 7: BP+OSD Decoder Through `ldpc`

**Files:**
- Modify: `src/qec_rd/kernel/decode.py`
- Test: `tests/test_decode_bposd.py`

- [ ] **Step 1: Write the failing BP+OSD test**

```python
# tests/test_decode_bposd.py
from qec_rd.api import (
    build_circuit,
    build_decoding_graph,
    extract_dem,
    run_decoder,
    sample_syndromes,
)
from qec_rd.core import CodeSpec, NoiseModel


def test_run_decoder_supports_bposd():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)
    batch = sample_syndromes(circuit, shots=8, seed=9)
    result = run_decoder(
        graph,
        batch,
        decoder_name="bposd",
        error_rate=1e-3,
        max_iter=8,
        osd_order=2,
    )

    assert result.decoder_name == "bposd"
    assert result.predicted_observables.shape == batch.observable_flips.shape
    assert result.corrections.shape[0] == 8
    assert result.failure_mask.shape == (8,)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_decode_bposd.py -v`

Expected: FAIL because the BP+OSD decoder adapter is not implemented.

- [ ] **Step 3: Implement the `ldpc` BP+OSD adapter**

```python
# src/qec_rd/kernel/decode.py
from __future__ import annotations

import numpy as np
from ldpc import BpOsdDecoder
from pymatching import Matching

from qec_rd.core import DecodeResult, DecoderConfigurationError, DecodingGraph, SyndromeBatch


def _run_pymatching(graph: DecodingGraph, batch: SyndromeBatch) -> DecodeResult:
    if graph.raw_dem_handle is None:
        raise DecoderConfigurationError("pymatching decoding requires a raw DEM handle.")
    matching = Matching.from_detector_error_model(graph.raw_dem_handle)
    predictions = np.asarray(matching.decode_batch(batch.detection_events), dtype=np.bool_)
    actual = batch.observable_flips
    if actual is None:
        failure_mask = np.zeros(batch.shot_count, dtype=np.bool_)
    else:
        failure_mask = np.any(predictions != actual, axis=1)
    return DecodeResult(
        decoder_name="pymatching",
        predicted_observables=predictions,
        actual_observables=actual,
        corrections=None,
        failure_mask=failure_mask,
        metadata={"backend": "pymatching"},
    )


def _run_bposd(
    graph: DecodingGraph,
    batch: SyndromeBatch,
    *,
    error_rate: float = 1e-3,
    max_iter: int = 8,
    osd_order: int = 2,
) -> DecodeResult:
    decoder = BpOsdDecoder(
        graph.check_matrix,
        error_rate=error_rate,
        bp_method="minimum_sum",
        schedule="serial",
        max_iter=max_iter,
        osd_method="osd_cs",
        osd_order=osd_order,
    )

    corrections = []
    predictions = []
    for syndrome in batch.detection_events.astype(np.uint8):
        correction = np.asarray(decoder.decode(syndrome), dtype=np.uint8)
        predicted = (graph.observable_matrix @ correction) % 2
        corrections.append(correction)
        predictions.append(predicted.astype(np.bool_))

    correction_array = np.asarray(corrections, dtype=np.uint8)
    prediction_array = np.asarray(predictions, dtype=np.bool_)
    actual = batch.observable_flips
    return normalize_custom_decode_result(
        decoder_name="bposd",
        predicted_observables=prediction_array,
        actual_observables=actual,
        corrections=correction_array,
        metadata={
            "backend": "ldpc.BpOsdDecoder",
            "error_rate": error_rate,
            "max_iter": max_iter,
            "osd_order": osd_order,
        },
    )


def run_decoder(
    graph: DecodingGraph,
    batch: SyndromeBatch,
    *,
    decoder_name: str,
    decoder_fn=None,
    **kwargs,
) -> DecodeResult:
    if decoder_name == "pymatching":
        return _run_pymatching(graph, batch)
    if decoder_name == "bposd":
        return _run_bposd(graph, batch, **kwargs)
    if decoder_name == "custom":
        if decoder_fn is None:
            raise DecoderConfigurationError("Custom decoding requires decoder_fn.")
        result = decoder_fn(graph, batch, **kwargs)
        if not isinstance(result, DecodeResult):
            raise DecoderConfigurationError("Custom decoder must return DecodeResult.")
        return result
    raise DecoderConfigurationError(f"Unsupported decoder: {decoder_name!r}")
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_decode_bposd.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/kernel/decode.py tests/test_decode_bposd.py
git commit -m "feat(decode): add ldpc bp-osd adapter"
```

---

### Task 7A: Custom Decoder End-to-End Hook

**Files:**
- Modify: `src/qec_rd/kernel/decode.py`
- Modify: `src/qec_rd/api.py`
- Test: `tests/test_decode_custom.py`

- [ ] **Step 1: Write the failing custom-decoder test**

```python
# tests/test_decode_custom.py
import numpy as np

from qec_rd.api import (
    analyze_results,
    build_circuit,
    build_decoding_graph,
    extract_dem,
    run_decoder,
    sample_syndromes,
)
from qec_rd.core import CodeSpec, DecodeResult, NoiseModel


def test_run_decoder_supports_custom_decoder_end_to_end():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)
    batch = sample_syndromes(circuit, shots=6, seed=13)

    def zero_decoder(graph, batch):
        return DecodeResult(
            decoder_name="zero_decoder",
            predicted_observables=np.zeros_like(batch.observable_flips, dtype=np.bool_),
            actual_observables=batch.observable_flips,
            corrections=np.zeros((batch.shot_count, graph.check_matrix.shape[1]), dtype=np.uint8),
            failure_mask=np.any(
                np.zeros_like(batch.observable_flips, dtype=np.bool_) != batch.observable_flips,
                axis=1,
            ),
            metadata={"kind": "custom"},
        )

    result = run_decoder(graph, batch, decoder_name="custom", decoder_fn=zero_decoder)
    report = analyze_results(result)

    assert result.decoder_name == "zero_decoder"
    assert report.shot_count == 6
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_decode_custom.py -v`

Expected: FAIL because the custom-decoder hook is not implemented or not exposed yet.

- [ ] **Step 3: Expose the custom-decoder hook in the API**

```python
# src/qec_rd/api.py
from qec_rd.core import CodeSpec, NoiseModel
from qec_rd.kernel.analysis import analyze_results
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.decode import normalize_custom_decode_result, run_decoder
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes

__all__ = [
    "analyze_results",
    "build_circuit",
    "build_decoding_graph",
    "extract_dem",
    "load_circuit",
    "normalize_custom_decode_result",
    "run_decoder",
    "sample_syndromes",
    "CodeSpec",
    "NoiseModel",
]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_decode_custom.py -v`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/kernel/decode.py src/qec_rd/api.py tests/test_decode_custom.py
git commit -m "feat(decode): add custom decoder hook"
```

---

### Task 8: Analysis Layer and End-to-End Pipeline Tests

**Files:**
- Modify: `src/qec_rd/kernel/analysis.py`
- Modify: `src/qec_rd/api.py`
- Create: `tests/conftest.py`
- Test: `tests/test_analysis.py`
- Test: `tests/integration/test_generated_pipeline.py`
- Test: `tests/integration/test_imported_pipeline.py`

- [ ] **Step 1: Write the failing analysis and integration tests**

```python
# tests/test_analysis.py
import numpy as np

from qec_rd.api import analyze_results
from qec_rd.core import DecodeResult


def test_analyze_results_computes_logical_error_rate():
    result = DecodeResult(
        decoder_name="pymatching",
        predicted_observables=np.zeros((10, 1), dtype=np.bool_),
        actual_observables=np.zeros((10, 1), dtype=np.bool_),
        corrections=None,
        failure_mask=np.array([False, False, True, False, False, True, False, False, False, False]),
        metadata={},
    )
    report = analyze_results(result)
    assert report.shot_count == 10
    assert report.failure_count == 2
    assert report.logical_error_rate == 0.2
```

```python
# tests/integration/test_generated_pipeline.py
from qec_rd.api import (
    analyze_results,
    build_circuit,
    build_decoding_graph,
    extract_dem,
    run_decoder,
    sample_syndromes,
)
from qec_rd.core import CodeSpec, NoiseModel


def test_generated_pipeline_runs_through_pymatching():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)
    batch = sample_syndromes(circuit, shots=16, seed=21)
    result = run_decoder(graph, batch, decoder_name="pymatching")
    report = analyze_results(result)
    assert report.decoder_name == "pymatching"
    assert report.shot_count == 16
```

```python
# tests/integration/test_imported_pipeline.py
from pathlib import Path

from qec_rd.api import (
    analyze_results,
    build_decoding_graph,
    extract_dem,
    load_circuit,
    run_decoder,
    sample_syndromes,
)


def test_imported_pipeline_runs_through_bposd(rep_code_stim_path: Path):
    circuit = load_circuit(rep_code_stim_path, format="stim")
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)
    batch = sample_syndromes(circuit, shots=8, seed=4)
    result = run_decoder(graph, batch, decoder_name="bposd", error_rate=1e-3, max_iter=8, osd_order=2)
    report = analyze_results(result)
    assert report.decoder_name == "bposd"
    assert report.shot_count == 8
```

- [ ] **Step 2: Add the missing fixture and run the tests to verify they fail**

```python
# tests/conftest.py
from pathlib import Path

import pytest
import stim


@pytest.fixture()
def rep_code_stim_path(tmp_path: Path) -> Path:
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        distance=3,
        rounds=3,
        after_clifford_depolarization=1e-3,
    )
    path = tmp_path / "rep_d3.stim"
    path.write_text(str(circuit), encoding="utf-8")
    return path
```

Run: `pytest tests/test_analysis.py tests/integration/test_generated_pipeline.py tests/integration/test_imported_pipeline.py -v`

Expected: FAIL because `analyze_results` is not implemented yet.

- [ ] **Step 3: Implement analysis**

```python
# src/qec_rd/kernel/analysis.py
from __future__ import annotations

import math

from qec_rd.core import AnalysisReport, DecodeResult


def analyze_results(result: DecodeResult | list[DecodeResult]) -> AnalysisReport:
    results = [result] if isinstance(result, DecodeResult) else result
    shot_count = sum(item.failure_mask.shape[0] for item in results)
    failure_count = sum(item.failure_count for item in results)
    logical_error_rate = failure_count / shot_count if shot_count else 0.0
    logical_error_rate_stderr = (
        math.sqrt(logical_error_rate * (1.0 - logical_error_rate) / shot_count)
        if shot_count
        else 0.0
    )
    decoder_name = results[0].decoder_name if results else "unknown"
    return AnalysisReport(
        decoder_name=decoder_name,
        shot_count=shot_count,
        failure_count=failure_count,
        logical_error_rate=logical_error_rate,
        logical_error_rate_stderr=logical_error_rate_stderr,
        metadata={"num_results": len(results)},
    )
```

```python
# src/qec_rd/api.py
from qec_rd.core import CodeSpec, NoiseModel
from qec_rd.kernel.analysis import analyze_results
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.decode import run_decoder
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes

__all__ = [
    "analyze_results",
    "build_circuit",
    "build_decoding_graph",
    "extract_dem",
    "load_circuit",
    "run_decoder",
    "sample_syndromes",
    "CodeSpec",
    "NoiseModel",
]
```

- [ ] **Step 4: Run the targeted tests and then the full suite**

Run: `pytest tests/test_analysis.py tests/integration/test_generated_pipeline.py tests/integration/test_imported_pipeline.py -v`

Expected: PASS with `3 passed`.

Run: `pytest -q`

Expected: PASS for the full suite, including the original `tests/test_stim_demo.py` and all new Stage 1 tests.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/kernel/analysis.py src/qec_rd/api.py tests/conftest.py tests/test_analysis.py tests/integration/test_generated_pipeline.py tests/integration/test_imported_pipeline.py
git commit -m "feat(analysis): add stage1 reports and end-to-end tests"
```

---

## Self-Review

### Spec coverage

- Unified object model: covered by Task 2
- Built-in rotated surface, unrotated surface, and toric support: covered by Tasks 2A and 3
- User-defined CSS code to simple stabilizer measurement circuit generation: covered by Tasks 2A and 3
- Stim-only Pauli-compatible noise scope: covered by Task 2
- Generated/imported circuit entry: covered by Task 3
- DEM extraction and decoding graph: covered by Task 4
- Fixed non-customizable DEM/graph behavior: covered by Task 4
- Stim sampling to standard batch: covered by Task 5
- Additional `SyndromeBatch` entry readiness: covered by Task 2 result-object design and Task 5 sampling normalization
- MWPM via external package: covered by Task 6
- BP+OSD via external package: covered by Task 7
- Custom decoder end-to-end hook: covered by Task 7A
- Basic analysis and end-to-end acceptance: covered by Task 8

### Placeholder scan

- No `TODO`, `TBD`, or deferred implementation markers remain in the tasks
- Every code-changing step includes explicit code
- Every verification step includes an exact command and expected outcome

### Type consistency

- `CodeSpec`, `NoiseModel`, `CircuitArtifact`, `DemArtifact`, `DecodingGraph`, `SyndromeBatch`, `DecodeResult`, and `AnalysisReport` are introduced in Task 2 and used consistently later
- `build_circuit`, `load_circuit`, `extract_dem`, `build_decoding_graph`, `sample_syndromes`, `run_decoder`, and `analyze_results` are introduced before they are used in later tasks
- Decoder names are kept consistent as `"pymatching"`, `"bposd"`, and `"custom"`
