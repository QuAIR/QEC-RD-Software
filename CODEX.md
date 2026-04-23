# CODEX.md

## Purpose

This file defines the working contract for Codex-style agents and human collaborators operating in `QEC-RD-Software`.

It is intentionally narrower than the long-form design specs. When there is a conflict:

1. explicit user instruction wins
2. approved Stage 1 specs and plans win
3. this file defines default repo-level behavior

## Current Project Phase

The repository is currently in **Stage 1 backbone construction**.

Stage 1 means:

- runtime backend is fixed to `stim`
- we are building the `qec_rd` backbone first
- we are not yet implementing TensorQEC runtime integration
- we are not yet implementing cloud or hardware deployment workflows

## Stage 1 Technical Constraints

### Backend

- `stim` is the only execution backend in Stage 1.
- Do not introduce a general multi-provider or multi-backend abstraction yet.

### Built-in circuit catalog support

Stage 1 built-in circuit entries must include:

- repetition code
- rotated surface code
- unrotated surface code
- toric code

In addition:

- `CodeSpec` should act as a built-in circuit selector/config object, not as a general user-defined code-definition interface
- user-facing research entry should center on circuits: generated built-in circuits or imported external circuits
- the built-in catalog should be extensible so future built-in families can be added without changing the backbone
- built-in surface and toric circuits should be generated through platform-owned code objects and platform-owned circuit builders, not through `stim.Circuit.generated(...)`
- `stim.Circuit.generated(...)` is not an acceptable shortcut for rotated surface, unrotated surface, or toric built-ins in Stage 1
- repetition code is the only family where `stim.Circuit.generated(...)` can be considered for narrow compatibility reasons, but a platform-owned object model is still preferred

### Noise model

- Stage 1 noise support is limited to **Stim-executable Pauli-like noise**.
- Do not add non-Pauli noise models in Stage 1.
- Do not add TensorQEC-style non-Pauli simulation paths in Stage 1.

### DEM and graph behavior

- DEM extraction and decoding-graph construction are **platform-owned fixed behavior** in Stage 1.
- They are not user-customizable extension points in this phase.

### Decoder policy

Stage 1 decoder support must include:

- MWPM via `pymatching`
- BP+OSD via `ldpc` / `bposd`
- custom decoder integration through the standard high-level decoder path

Decoder rules:

- do not implement MWPM manually in this repository
- do not implement BP+OSD manually in this repository
- use common external packages
- normalize all decoder outputs into `DecodeResult`
- custom decoders must be able to continue into `AnalysisReport`

### Data-entry policy

- circuit entry must support both generated circuits and imported circuits
- Stage 1 public API should expose both the direct pipeline API and a DeltaKit-style runner API
- `SyndromeBatch` should remain open to future external data-entry paths
- analysis should remain extensible for future research workflows

## Expected Package Direction

Stage 1 work should align with the approved backbone:

- `qec_rd.core`
- `qec_rd.adapters.stim`
- `qec_rd.kernel.circuit`
- `qec_rd.kernel.graph`
- `qec_rd.kernel.decode`
- `qec_rd.kernel.runner`
- `qec_rd.kernel.analysis`
- `qec_rd.api`

Avoid introducing unrelated package structure until the Stage 1 backbone is in place.

## Engineering Workflow

Before major implementation:

- prefer writing or updating specs and plans first
- keep work aligned with `docs/superpowers/specs/`
- keep execution aligned with `docs/superpowers/plans/`

During implementation:

- prefer TDD or test-first increments
- keep changes scoped to the current task
- preserve end-to-end backbone semantics
- avoid speculative abstraction

## Testing Expectations

Every substantive Stage 1 change should strengthen one or more of these:

- core object model tests
- built-in circuit generation tests
- imported circuit tests
- DEM / graph tests
- MWPM decoder adapter tests
- BP+OSD decoder adapter tests
- custom decoder hook tests
- analysis tests
- end-to-end pipeline tests

Do not claim Stage 1 success without end-to-end coverage.

## Documentation Expectations

When architecture or execution rules change:

- update the relevant spec in `docs/superpowers/specs/`
- update the relevant plan in `docs/superpowers/plans/`
- keep `CODEX.md` and `AGENTS.md` in sync when repo-level working rules change

## Things To Avoid

- adding non-Pauli runtime behavior into Stage 1
- adding user-customizable DEM / graph strategy in Stage 1
- introducing plugin systems prematurely
- bypassing platform objects with backend-native objects as public API
- silently expanding Stage 1 scope
