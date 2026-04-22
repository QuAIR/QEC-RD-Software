# Workstream B: DEM, Graph, and Sampling Implementation Plan

> **Owner:** Lei Zhang (lei zhang)  
> **Branch:** `workstream-b`  
> **Date:** 2026-04-22  
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the Stage 1 DEM extraction, decoding graph construction, and Stim sampling backbone for `qec_rd`, consuming frozen circuit artifacts from Workstream A and producing stable `DecodingGraph` and `SyndromeBatch` objects for Workstream C.

**Architecture:** This plan executes Task 3 (Workstream B assignment) from the three-person execution plan, covering Task 4 (DEM/graph) and Task 5 (sampling) from the Stage 1 backbone implementation plan. DEM and graph behavior remain platform-owned and fixed per Stage 1 constraints. No user-customizable DEM/graph strategy is introduced.

**Tech Stack:** Python 3.10+, `stim`, `numpy`, `scipy`, `pytest`

---

## File Ownership

### Owned source files
- `src/qec_rd/kernel/graph.py`
  DEM extraction, decoding graph construction, and sampling orchestration.
- `src/qec_rd/adapters/stim.py` (sampling and DEM bridge portions)
  Stim-native bridge for `extract_stim_dem` and `sample_stim_detectors`.
- `src/qec_rd/core/artifacts.py` (graph-facing fields)
  `DemArtifact` and `DecodingGraph` dataclass definitions.

### Owned test files
- `tests/test_dem_graph.py`
  DEM extraction and decoding graph construction tests.
- `tests/test_sampling.py`
  Stim sampling to `SyndromeBatch` tests.

### Consumed from Workstream A (frozen contract)
- `src/qec_rd/core/types.py` — `CircuitSourceKind`, exceptions
- `src/qec_rd/core/codes.py` — `CodeSpec`
- `src/qec_rd/core/noise.py` — `NoiseModel`
- `src/qec_rd/core/results.py` — `SyndromeBatch`
- `src/qec_rd/kernel/circuit.py` — `build_circuit`, `load_circuit`
- `src/qec_rd/api.py` — public API re-exports

### Produced for Workstream C (downstream contract)
- `DecodingGraph` — stable graph object with check matrix, observable matrix, error probabilities
- `SyndromeBatch` — standardized sampling output with detection events and observable flips
- `DemArtifact` — intermediate DEM artifact with detector/observable counts

---

## Interface Freeze

Workstream B builds against the following frozen shared objects. These must not be redefined locally:

- `CircuitArtifact` — input to DEM extraction and sampling
- `DemArtifact` — output of DEM extraction, input to graph construction
- `DecodingGraph` — output of graph construction
- `SyndromeBatch` — output of sampling

Freeze rules for Workstream B:
- add fields only if Workstream A (owning object model) and Workstream C (downstream consumer) agree
- do not rename public fields after downstream work has started
- do not expose `stim.DetectorErrorModel` or `stim.CompiledDetectorSampler` as public API language
- do not make DEM extraction or graph construction user-customizable

---

## Task 1: Scaffold Workstream B Module Files

**Files:**
- Create: `src/qec_rd/kernel/graph.py`
- Modify: `src/qec_rd/adapters/stim.py` (add DEM and sampling bridge functions)
- Create: `tests/test_dem_graph.py`
- Create: `tests/test_sampling.py`

- [ ] **Step 1: Write the failing import and stub tests**

Expected output:
- `tests/test_dem_graph.py` imports and calls `extract_dem`, `build_decoding_graph`
- `tests/test_sampling.py` imports and calls `sample_syndromes`
- both tests fail with `ImportError` or `AttributeError`

- [ ] **Step 2: Create module stubs and adapter functions**

Stub contents:
- `src/qec_rd/kernel/graph.py` — empty module docstring `"""DEM and graph logic."""`
- `src/qec_rd/adapters/stim.py` — add placeholder `extract_stim_dem` and `sample_stim_detectors`

- [ ] **Step 3: Verify tests still fail with clear missing-implementation errors**

Run: `pytest tests/test_dem_graph.py tests/test_sampling.py -v`

Expected: FAIL with clear "not implemented" or `AttributeError` messages.

- [ ] **Step 4: Commit the scaffold**

```bash
git add src/qec_rd/kernel/graph.py src/qec_rd/adapters/stim.py tests/test_dem_graph.py tests/test_sampling.py
git commit -m "build: scaffold workstream b dem, graph, and sampling modules"
```

---

## Task 2: Implement DEM Extraction

**Files:**
- Modify: `src/qec_rd/adapters/stim.py` — add `extract_stim_dem`
- Modify: `src/qec_rd/kernel/graph.py` — add `extract_dem`
- Modify: `src/qec_rd/api.py` — re-export `extract_dem`
- Test: `tests/test_dem_graph.py`

**Assumed frozen inputs from Workstream A:**
- `CircuitArtifact` with `raw_handle` field caching a `stim.Circuit`
- `CircuitArtifact` carrying `source_kind`, `source_format`, `origin_metadata`

- [ ] **Step 1: Write the failing DEM extraction test**

```python
# tests/test_dem_graph.py
def test_extract_dem_returns_dem_artifact():
    from qec_rd.api import build_circuit, extract_dem
    from qec_rd.core import CodeSpec, NoiseModel

    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)

    assert dem.num_detectors > 0
    assert dem.num_observables >= 1
    assert dem.dem_text
    assert dem.raw_handle is not None
```

Run: `pytest tests/test_dem_graph.py -v`

Expected: FAIL because `extract_dem` is not implemented.

- [ ] **Step 2: Implement Stim DEM extraction bridge**

```python
# src/qec_rd/adapters/stim.py
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

Rules:
- `decompose_errors=True` is required for Stage 1 graphlike DEM terms
- the raw `stim.DetectorErrorModel` is cached in `raw_handle` but not exposed as public API

- [ ] **Step 3: Implement `extract_dem` in graph kernel**

```python
# src/qec_rd/kernel/graph.py
def extract_dem(circuit_artifact: CircuitArtifact) -> DemArtifact:
    return extract_stim_dem(circuit_artifact)
```

- [ ] **Step 4: Wire `extract_dem` into public API**

Add `extract_dem` to `src/qec_rd/api.py` imports and `__all__`.

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/test_dem_graph.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/qec_rd/adapters/stim.py src/qec_rd/kernel/graph.py src/qec_rd/api.py tests/test_dem_graph.py
git commit -m "feat(graph): add dem extraction from circuit artifacts"
```

---

## Task 3: Implement Decoding Graph Construction

**Files:**
- Modify: `src/qec_rd/kernel/graph.py` — add `build_decoding_graph`
- Modify: `src/qec_rd/api.py` — re-export `build_decoding_graph`
- Test: `tests/test_dem_graph.py`

**Assumed frozen inputs:**
- `DemArtifact` with `num_detectors`, `num_observables`, `raw_handle`

**Required downstream contract for Workstream C:**
- `DecodingGraph` fields must be stable: `num_detectors`, `num_observables`, `check_matrix`, `observable_matrix`, `error_probabilities`, `edge_fault_ids`, `raw_dem_handle`
- `kernel.decode` must consume `DecodingGraph` without reaching back into raw Stim-native objects

- [ ] **Step 1: Write the failing graph construction test**

```python
# tests/test_dem_graph.py
def test_build_decoding_graph_from_dem_artifact():
    import numpy as np
    from scipy.sparse import csc_matrix
    from qec_rd.api import build_circuit, build_decoding_graph, extract_dem
    from qec_rd.core import CodeSpec, NoiseModel

    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)

    assert graph.num_detectors == dem.num_detectors
    assert graph.num_observables == dem.num_observables
    assert graph.check_matrix.shape[0] == dem.num_detectors
    assert isinstance(graph.check_matrix, csc_matrix)
    assert isinstance(graph.observable_matrix, np.ndarray)
    assert np.all(graph.error_probabilities > 0.0)
    assert len(graph.edge_fault_ids) == graph.check_matrix.shape[1]
```

Run: `pytest tests/test_dem_graph.py -v`

Expected: FAIL because `build_decoding_graph` is not implemented.

- [ ] **Step 2: Implement graph construction**

```python
# src/qec_rd/kernel/graph.py
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
            raise UnsupportedDemError(
                "Stage 1 only supports graphlike DEM terms with up to two detectors."
            )
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
    observable_matrix = np.zeros(
        (dem_artifact.num_observables, column), dtype=np.uint8
    )
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

Stage 1 rules enforced:
- skip non-error DEM instructions
- skip errors with no detectors (boundary-only terms are not graph edges)
- reject hypergraph terms with more than 2 detectors (`UnsupportedDemError`)
- build sparse check matrix in CSC format
- build dense observable matrix

- [ ] **Step 3: Wire `build_decoding_graph` into public API**

Add `build_decoding_graph` to `src/qec_rd/api.py` imports and `__all__`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_dem_graph.py -v`

Expected: PASS for both DEM extraction and graph tests.

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/kernel/graph.py src/qec_rd/api.py tests/test_dem_graph.py
git commit -m "feat(graph): add decoding graph construction from dem artifact"
```

---

## Task 4: Implement Stim Sampling into `SyndromeBatch`

**Files:**
- Modify: `src/qec_rd/adapters/stim.py` — add `sample_stim_detectors`
- Modify: `src/qec_rd/kernel/graph.py` — add `sample_syndromes`
- Modify: `src/qec_rd/api.py` — re-export `sample_syndromes`
- Test: `tests/test_sampling.py`

**Assumed frozen inputs from Workstream A:**
- `CircuitArtifact` with `raw_handle` caching a `stim.Circuit`

**Required downstream contract for Workstream C:**
- `SyndromeBatch` fields must be stable: `detection_events`, `observable_flips`, `measurements`, `shot_count`, `seed`, `source`
- `detection_events` and `observable_flips` must be `np.ndarray` with `dtype=np.bool_`

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
    assert batch.source == "stim.detector_sampler"


def test_sample_syndromes_varies_with_seed():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    batch_a = sample_syndromes(circuit, shots=4, seed=1)
    batch_b = sample_syndromes(circuit, shots=4, seed=2)
    assert not np.array_equal(batch_a.detection_events, batch_b.detection_events)
```

Run: `pytest tests/test_sampling.py -v`

Expected: FAIL because `sample_syndromes` is not implemented.

- [ ] **Step 2: Implement Stim sampling bridge**

```python
# src/qec_rd/adapters/stim.py
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

Rules:
- `separate_observables=True` returns observable flips alongside detection events
- `measurements` is `None` in Stage 1 (raw measurements not stored by default)
- dtype normalization to `np.bool_` ensures downstream contract stability

- [ ] **Step 3: Implement `sample_syndromes` in graph kernel**

```python
# src/qec_rd/kernel/graph.py
def sample_syndromes(
    circuit_artifact: CircuitArtifact,
    *,
    shots: int,
    seed: int | None = None,
) -> SyndromeBatch:
    return sample_stim_detectors(circuit_artifact, shots=shots, seed=seed)
```

- [ ] **Step 4: Wire `sample_syndromes` into public API**

Add `sample_syndromes` to `src/qec_rd/api.py` imports and `__all__`.

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/test_sampling.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/qec_rd/adapters/stim.py src/qec_rd/kernel/graph.py src/qec_rd/api.py tests/test_sampling.py
git commit -m "feat(sampling): add stim syndrome batch sampling"
```

---

## Task 5: Validate Workstream B Slice Isolation

**Files:**
- Review: `src/qec_rd/kernel/graph.py`
- Review: `src/qec_rd/adapters/stim.py`
- Review: `tests/test_dem_graph.py`
- Review: `tests/test_sampling.py`

- [ ] **Step 1: Run the owned test suite**

Run: `pytest tests/test_dem_graph.py tests/test_sampling.py -v`

Expected: PASS for all Workstream B owned tests.

- [ ] **Step 2: Verify no scope drift**

Checklist:
- [ ] `kernel.graph` does not implement decoder logic (no `pymatching`, no `ldpc` imports)
- [ ] `kernel.graph` does not implement analysis logic (no logical error rate computation)
- [ ] `kernel.graph` does not implement circuit generation logic (no `stim.Circuit.generated` calls)
- [ ] `kernel.graph` does not add new public abstractions beyond `extract_dem`, `build_decoding_graph`, `sample_syndromes`
- [ ] DEM extraction and graph construction are not exposed as user-customizable strategies
- [ ] no non-Pauli runtime behavior is introduced

- [ ] **Step 3: Verify dependency direction is respected**

Checklist:
- [ ] `kernel.graph` depends on `core` objects (allowed)
- [ ] `kernel.graph` depends on `adapters.stim` (allowed)
- [ ] `kernel.graph` does not depend on `kernel.decode`, `kernel.analysis`, or `kernel.runner`
- [ ] `core` does not depend on `kernel.graph`

- [ ] **Step 4: Run a quick integration sanity check with Workstream A outputs**

Run:
```bash
pytest tests/test_circuit_entry.py tests/test_dem_graph.py tests/test_sampling.py -v
```

Expected: PASS — Workstream A circuit entry flows cleanly into Workstream B DEM/graph/sampling.

- [ ] **Step 5: Final commit for Workstream B slice**

```bash
git add docs/superpowers/plans/2026-04-22-qec-rd-workstream-b-plan.md
git commit -m "docs: add workstream b implementation plan"
```

---

## Task 6: Handoff Checklist for Workstream C

Before Workstream B branch is considered ready for integration:

- [ ] `extract_dem(CircuitArtifact) -> DemArtifact` is implemented and tested
- [ ] `build_decoding_graph(DemArtifact) -> DecodingGraph` is implemented and tested
- [ ] `sample_syndromes(CircuitArtifact, shots, seed) -> SyndromeBatch` is implemented and tested
- [ ] `DecodingGraph` fields are stable and documented:
  - `num_detectors: int`
  - `num_observables: int`
  - `check_matrix: csc_matrix` — shape `(num_detectors, num_edges)`
  - `observable_matrix: np.ndarray` — shape `(num_observables, num_edges)`
  - `error_probabilities: np.ndarray` — shape `(num_edges,)`
  - `edge_fault_ids: list[int]` — column index mapping
  - `raw_dem_handle: Any | None` — cached native DEM, not public API
- [ ] `SyndromeBatch` fields are stable and documented:
  - `detection_events: np.ndarray` — shape `(shots, num_detectors)`, dtype `bool`
  - `observable_flips: np.ndarray | None` — shape `(shots, num_observables)`, dtype `bool`
  - `measurements: np.ndarray | None` — `None` in Stage 1
  - `shot_count: int`
  - `seed: int | None`
  - `source: str`
- [ ] all Workstream B owned tests pass
- [ ] no `TODO`, `TBD`, or deferred placeholders remain in Workstream B code
- [ ] commits are readable and narrow (one task per commit)

---

## Integration Notes

### Merge order
Workstream B merges after Workstream A and before Workstream C.

Preferred branch: `codex/stage1-graph-sampling`

### Integration tests to run after merge
```bash
pytest tests/integration/test_generated_pipeline.py -v
pytest tests/integration/test_imported_pipeline.py -v
```

These integration tests verify that the DEM/graph/sampling backbone correctly connects circuit entry (Workstream A) to decoding/analysis (Workstream C).

### Interface drift resolution
If Workstream A renames `CircuitArtifact` fields or changes `raw_handle` semantics before merge, Workstream B must update `extract_dem` and `sample_syndromes` to match. If Workstream C requires additional `DecodingGraph` or `SyndromeBatch` fields, all three workstreams must agree before changes are made.

---

## Self-Review

### Spec coverage
- DEM extraction from `CircuitArtifact`: covered by Task 2
- Decoding graph construction as fixed platform behavior: covered by Task 3
- `DecodingGraph` object contract for downstream decode: covered by Task 3 and Task 6 handoff
- Stim sampling normalized to `SyndromeBatch`: covered by Task 4
- No user-customizable DEM/graph strategy: enforced in Tasks 2, 3, 5
- No non-Pauli runtime behavior: enforced in Task 5

### Placeholder scan
- No `TODO`, `TBD`, or deferred implementation markers remain
- Every step has explicit files, actions, and expected outcomes
- Verification commands are concrete

### Type consistency
- `CircuitArtifact` is consumed, not redefined
- `DemArtifact` is produced and consumed within Workstream B
- `DecodingGraph` is produced for Workstream C
- `SyndromeBatch` is produced for Workstream C
- `extract_dem`, `build_decoding_graph`, `sample_syndromes` signatures align with Stage 1 API spec
