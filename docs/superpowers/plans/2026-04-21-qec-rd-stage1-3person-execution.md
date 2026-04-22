# QEC-RD Stage 1 Three-Person Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the approved Stage 1 `qec_rd` backbone with three contributors working in parallel without drifting from the agreed architecture or blocking each other on unclear ownership.

**Architecture:** This is a delivery-harness plan layered on top of the approved Stage 1 product plan. The product architecture remains unchanged: `stim` stays the only runtime backend, the user-facing abstraction stays circuit-first, the direct pipeline API remains public, and the DeltaKit-style runner shell is added on top. This plan defines how three contributors divide the repo, which interfaces must be treated as frozen before parallel work starts, and how integration should happen.

**Tech Stack:** Git, GitHub, Python 3.10+, `pytest`, repo docs in `docs/superpowers/`, Stage 1 backbone modules under `src/qec_rd/`

---

## File Structure

### Planning and coordination files

- `docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design-en.md`
  Stage 1 architecture source of truth in English.
- `docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design.md`
  Chinese version of the Stage 1 architecture source of truth.
- `docs/superpowers/plans/2026-04-20-qec-rd-stage1-backbone-implementation.md`
  Product implementation plan for the Stage 1 backbone.
- `docs/superpowers/plans/2026-04-21-qec-rd-stage1-3person-execution.md`
  This execution and ownership plan for three contributors.
- `AGENTS.md`
  Repo-level constraints, delegation boundaries, and Stage 1 guardrails.
- `CODEX.md`
  Repo-level working contract and implementation expectations.

### Product workstream ownership zones

- Workstream A: `src/qec_rd/core/`, `src/qec_rd/kernel/circuit.py`, circuit-loading portions of `src/qec_rd/adapters/stim.py`, and circuit-entry tests.
- Workstream B: `src/qec_rd/kernel/graph.py`, graph-related structures in `src/qec_rd/core/artifacts.py`, sampling flow, and graph/sampling tests.
- Workstream C: `src/qec_rd/kernel/decode.py`, `src/qec_rd/kernel/analysis.py`, `src/qec_rd/kernel/runner.py`, `src/qec_rd/api.py`, and decode/analysis/runner tests.

---

## Interface Freeze

These interfaces must be treated as the Stage 1 integration contract before parallel coding begins:

- `CodeSpec`
- `ExperimentConfig`
- `CircuitArtifact`
- `DemArtifact`
- `DecodingGraph`
- `SyndromeBatch`
- `DecodeResult`
- `AnalysisReport`
- `ExperimentResult`

The freeze rule for Stage 1 parallel work:

- contributors may add fields only if the owning workstream agrees and downstream users are updated in the same branch
- contributors must not rename public fields casually after another workstream has started using them
- contributors must not expose backend-native objects as the public API language
- contributors must not reopen non-Pauli runtime behavior, DEM customization, or provider/plugin architecture

---

### Task 1: Lock the Shared Contract Before Parallel Work

**Files:**
- Review: `docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design-en.md`
- Review: `docs/superpowers/plans/2026-04-20-qec-rd-stage1-backbone-implementation.md`
- Review: `AGENTS.md`
- Review: `CODEX.md`

- [ ] **Step 1: Confirm the Stage 1 non-negotiables**

Use this checklist:

- backend is only `stim`
- user-facing abstraction is circuit-first
- built-in circuit catalog includes repetition, rotated surface, unrotated surface, and toric
- direct pipeline API remains public
- DeltaKit-style runner API is added on top
- DEM and graph logic stay fixed and platform-owned
- MWPM and BP+OSD come from external packages

- [ ] **Step 2: Freeze the shared object contract**

Use this shared contract list:

- `CodeSpec`
- `ExperimentConfig`
- `CircuitArtifact`
- `DemArtifact`
- `DecodingGraph`
- `SyndromeBatch`
- `DecodeResult`
- `AnalysisReport`
- `ExperimentResult`

Expected outcome: all three contributors agree to build against these names and object roles before parallel coding begins.

- [ ] **Step 3: Record open questions only if they block multiple workstreams**

Good blocking questions:

- does `ExperimentConfig` accept only core objects, only dict-like specs, or both
- which module owns source metadata normalization for imported circuits
- whether `SyndromeBatch` must always include observables in Stage 1

Bad non-blocking questions:

- style-only naming preferences inside one private helper
- future provider abstractions
- non-Stage-1 roadmap ideas

- [ ] **Step 4: Start parallel work only after the contract is frozen**

Expected outcome: no contributor begins on their lane while still assuming different object shapes.

---

### Task 2: Assign Workstream A - Core Objects and Circuit Entry

**Files:**
- Own: `src/qec_rd/core/types.py`
- Own: `src/qec_rd/core/codes.py`
- Own: `src/qec_rd/core/noise.py`
- Own: `src/qec_rd/core/artifacts.py` for circuit-facing fields
- Own: `src/qec_rd/core/results.py` only where object definitions are needed for shared contracts
- Own: `src/qec_rd/core/experiments.py` for shared experiment-level dataclasses
- Own: `src/qec_rd/kernel/circuit.py`
- Own: circuit-loading parts of `src/qec_rd/adapters/stim.py`
- Own tests: `tests/test_core_models.py`, `tests/test_builtin_codes.py`, `tests/test_builtin_catalog.py`, `tests/test_circuit_entry.py`

- [ ] **Step 1: Deliver the shared dataclasses and enums first**

Expected output:

- importable core object layer
- constructor-level validation for built-in circuit catalog entries
- object metadata shape stable enough for downstream graph/decode work

- [ ] **Step 2: Deliver circuit entry next**

Expected output:

- `build_circuit(...)`
- `load_circuit(...)`
- built-in repetition/surface/toric circuit generation
- imported `stim.Circuit` and `.stim` support

- [ ] **Step 3: Avoid stepping into graph/decode policy**

Workstream A should not decide:

- DEM-to-graph transformation policy
- decoder adapter internals
- analysis policy

- [ ] **Step 4: Publish the object and circuit-entry branch only when tests pass for this slice**

Required verification:

- `pytest tests/test_core_models.py tests/test_builtin_codes.py tests/test_builtin_catalog.py tests/test_circuit_entry.py -v`

Expected: PASS for the owned slice before merge request or handoff.

---

### Task 3: Assign Workstream B - DEM, Graph, and Sampling

**Files:**
- Own: `src/qec_rd/kernel/graph.py`
- Own: graph-facing fields in `src/qec_rd/core/artifacts.py`
- Own: sampling normalization in `src/qec_rd/adapters/stim.py` and/or `src/qec_rd/kernel/graph.py` as chosen by the product plan
- Own tests: `tests/test_dem_graph.py`, `tests/test_sampling.py`

- [ ] **Step 1: Build only against the frozen circuit artifacts**

Inputs Workstream B may assume exist:

- `CircuitArtifact`
- `DemArtifact`
- `DecodingGraph`
- `SyndromeBatch`

Workstream B should not redefine them locally.

- [ ] **Step 2: Implement fixed Stage 1 DEM and graph behavior**

Expected output:

- `extract_dem(...)`
- `build_decoding_graph(...)`
- `sample_syndromes(...)`

Stage 1 rule:

- this logic is platform-owned and not user-customizable

- [ ] **Step 3: Keep graph semantics stable for decoder consumers**

Required downstream contract:

- `kernel.decode` must be able to consume `DecodingGraph` and `SyndromeBatch` without reaching back into raw Stim-native objects

- [ ] **Step 4: Publish the graph/sampling branch only when tests pass for this slice**

Required verification:

- `pytest tests/test_dem_graph.py tests/test_sampling.py -v`

Expected: PASS for the owned slice before merge request or handoff.

---

### Task 4: Assign Workstream C - Decode, Analysis, and Runner API

**Files:**
- Own: `src/qec_rd/kernel/decode.py`
- Own: `src/qec_rd/kernel/analysis.py`
- Own: `src/qec_rd/kernel/runner.py`
- Own: `src/qec_rd/api.py`
- Own tests: `tests/test_decode_pymatching.py`, `tests/test_decode_bposd.py`, `tests/test_decode_custom.py`, `tests/test_analysis.py`, `tests/test_experiment_runner.py`, `tests/integration/test_runner_pipeline.py`

- [ ] **Step 1: Build decoder adapters against frozen graph/runtime objects**

Required inputs:

- `DecodingGraph`
- `SyndromeBatch`

Required outputs:

- `DecodeResult`

- [ ] **Step 2: Deliver analysis on top of normalized decode outputs**

Required output:

- `AnalysisReport`

Workstream C should not bypass decode normalization and read backend-native data directly.

- [ ] **Step 3: Deliver the runner shell only after direct pipeline pieces are usable**

Required output:

- `ExperimentRunner`
- `run_experiment(...)`
- `benchmark(...)`
- `sweep(...)`

Runner rule:

- the runner must reuse the same backbone artifacts and semantics as the direct pipeline API

- [ ] **Step 4: Publish the decode/analysis/runner branch only when tests pass for this slice**

Required verification:

- `pytest tests/test_decode_pymatching.py tests/test_decode_bposd.py tests/test_decode_custom.py tests/test_analysis.py tests/test_experiment_runner.py tests/integration/test_runner_pipeline.py -v`

Expected: PASS for the owned slice before merge request or handoff.

---

### Task 5: Integrate in Dependency Order

**Files:**
- Review: `src/qec_rd/core/`
- Review: `src/qec_rd/kernel/circuit.py`
- Review: `src/qec_rd/kernel/graph.py`
- Review: `src/qec_rd/kernel/decode.py`
- Review: `src/qec_rd/kernel/analysis.py`
- Review: `src/qec_rd/kernel/runner.py`
- Review: `src/qec_rd/api.py`
- Review: `tests/integration/test_generated_pipeline.py`
- Review: `tests/integration/test_imported_pipeline.py`
- Review: `tests/integration/test_runner_pipeline.py`

- [ ] **Step 1: Merge the contract-owning work first**

Preferred order:

1. Workstream A
2. Workstream B
3. Workstream C

Reason:

- circuit-entry and object contracts unblock graph work
- graph/sampling unblocks decode and runner work

- [ ] **Step 2: Run integration tests after each merge wave**

Required commands:

- `pytest tests/integration/test_generated_pipeline.py -v`
- `pytest tests/integration/test_imported_pipeline.py -v`
- `pytest tests/integration/test_runner_pipeline.py -v`

Expected: each path stays green as integration progresses.

- [ ] **Step 3: Resolve interface drift immediately, not later**

Examples of integration blockers that must be fixed before moving on:

- renamed fields in `DecodingGraph`
- changed `DecodeResult` properties without updating analysis
- runner API expecting dict specs while core tests assume object specs only

- [ ] **Step 4: Do the full-suite run only after all three workstreams have landed**

Required command:

- `pytest -q`

Expected: PASS for the entire Stage 1 test suite.

---

### Task 6: Apply Merge and Review Discipline

**Files:**
- Review: `AGENTS.md`
- Review: `CODEX.md`
- Review: `docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design-en.md`
- Review: `docs/superpowers/plans/2026-04-20-qec-rd-stage1-backbone-implementation.md`

- [ ] **Step 1: Use one focused branch per workstream**

Recommended branch themes:

- `codex/stage1-core-circuit`
- `codex/stage1-graph-sampling`
- `codex/stage1-decode-runner`

- [ ] **Step 2: Keep commits readable and narrow**

Good commit shape:

- scaffold core objects
- add built-in circuit catalog entry tests
- implement graph extraction
- add pymatching adapter
- add runner API

Bad commit shape:

- "finish stage1"
- "large refactor"
- mixed architecture cleanup plus decoder changes plus doc rewrites

- [ ] **Step 3: Reject out-of-scope expansion during Stage 1**

Do not merge branches that also try to add:

- non-Pauli runtime behavior
- provider abstraction
- DEM customization
- in-repo decoder reimplementation
- new public abstractions that bypass the agreed object chain

- [ ] **Step 4: Require tests with each mergeable slice**

Minimum merge gate:

- each workstream branch proves its owned tests pass
- integration owner proves relevant end-to-end path still passes

---

### Task 7: Close Stage 1 with an Explicit Acceptance Pass

**Files:**
- Review: `docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design-en.md`
- Review: `docs/superpowers/plans/2026-04-20-qec-rd-stage1-backbone-implementation.md`
- Review: `tests/integration/test_generated_pipeline.py`
- Review: `tests/integration/test_imported_pipeline.py`
- Review: `tests/integration/test_runner_pipeline.py`

- [ ] **Step 1: Verify the generated-circuit path**

Acceptance target:

- built-in circuit catalog entry flows through the full backbone

- [ ] **Step 2: Verify the imported-circuit path**

Acceptance target:

- imported `.stim` or `stim.Circuit` flows through the same backbone

- [ ] **Step 3: Verify decoder coverage**

Acceptance target:

- MWPM path passes
- BP+OSD path passes
- custom decoder hook passes

- [ ] **Step 4: Verify runner coverage**

Acceptance target:

- `run_experiment(...)` works
- `benchmark(...)` works
- `sweep(...)` works
- runner path reuses the same backbone semantics as direct pipeline use

- [ ] **Step 5: Verify docs still match the final implementation**

Required docs:

- `AGENTS.md`
- `CODEX.md`
- Stage 1 spec
- Stage 1 implementation plan

Expected: no merged implementation branch leaves repo-level docs behind.

---

## Self-Review

### Spec coverage

- Three-person ownership boundaries: covered by Tasks 2, 3, and 4
- Frozen shared interface contract: covered by Task 1
- Parallelizable workstream design: covered by Tasks 2, 3, and 4
- Integration order and dependency handling: covered by Task 5
- Merge discipline without scope drift: covered by Task 6
- Final Stage 1 acceptance check: covered by Task 7
- No pressure-creating cadence rules: intentionally omitted from this execution plan

### Placeholder scan

- No `TODO`, `TBD`, or deferred placeholders remain
- Each task has explicit files, actions, and expected outcomes
- Verification commands are concrete where command execution is part of the work

### Type consistency

- Workstream A owns shared object and circuit-entry definitions first
- Workstream B consumes circuit artifacts and produces graph/runtime objects
- Workstream C consumes graph/runtime objects and produces decode/analysis/runner outputs
- The runner layer is explicitly downstream of the direct pipeline, not a competing backbone
