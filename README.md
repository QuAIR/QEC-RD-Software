# QEC-RD-Software

<p align="center">
  <img src="assets/logos/qec-rd-logo-primary.png" alt="QEC-RD logo" width="520">
</p>

[![CI](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/ci.yml/badge.svg)](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/ci.yml)
[![Coverage](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/coverage.yml/badge.svg)](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/coverage.yml)
[![codecov](https://codecov.io/gh/QuAIR/QEC-RD-Software/branch/main/graph/badge.svg)](https://codecov.io/gh/QuAIR/QEC-RD-Software)
[![Docs](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/docs.yml/badge.svg)](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/docs.yml)

QEC-RD-Software is a research and engineering platform for quantum error correction (QEC).

The project is aimed at building a practical local backbone that connects circuit construction, detector-error-model (DEM) extraction, syndrome sampling, decoding, and analysis inside one coherent workflow. Our current Stage 1 direction is to establish a clean `qec_rd` backbone on top of `stim`, while keeping the architecture extensible enough for future research and engineering growth.

## Vision

We want this repository to become a bridge from QEC theory exploration to engineering-oriented research. Instead of treating circuit generation, DEM handling, decoding, and analysis as isolated scripts, the project is organized around a unified platform object chain and a reproducible development workflow.

In Stage 1, the runtime backend is intentionally narrow:

- `stim` is the only execution backend
- DEM and graph behavior are fixed and platform-owned
- non-Pauli runtime behavior is out of scope
- decoder algorithms come from standard external packages or custom decoder hooks

## Target Features

The current product plans and execution plans are organized around the following core capabilities:

1. Built-in circuit catalog generation for repetition, rotated surface, unrotated surface, and toric families.
2. Circuit import as the main customization path, so researchers can bring in external `stim` circuits and future circuit formats.
3. Fixed DEM extraction from circuits into platform-standard artifacts.
4. Fixed decoding-graph construction that downstream decoders can consume through stable platform objects.
5. Stim-based syndrome sampling normalized into a standard `SyndromeBatch`.
6. Stim-compatible Pauli noise presets, including toy, toy phenomenological, SD6, and SI1000-without-leakage models.
7. External decoder integration for MWPM and BP+OSD through common ecosystem packages instead of in-repo decoder reimplementation.
8. Custom decoder hooks that let user-defined decoders join the same end-to-end pipeline and analysis flow.

## Stage 1 Backbone

The approved Stage 1 architecture centers on a unified object chain:

`CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`

This backbone is intended to give the project a stable scientific kernel that stays inside `qec_rd`, instead of exposing backend-native objects as the public language of the platform.

Planned Stage 1 module layout:

- `src/qec_rd/core/`
  Shared object model, types, artifacts, experiment-level data structures, and result containers.
- `src/qec_rd/kernel/circuit.py`
  Built-in circuit catalog generation and external circuit import.
- `src/qec_rd/kernel/graph.py`
  DEM extraction, decoding-graph construction, and syndrome sampling flow.
- `src/qec_rd/kernel/decode.py`
  Decoder adaptation for MWPM, BP+OSD, and custom decoders.
- `src/qec_rd/kernel/analysis.py`
  Research-facing analysis and logical error rate reporting.
- `src/qec_rd/adapters/stim.py`
  Low-level bridge between platform objects and `stim`.
- `src/qec_rd/api.py`
  Thin public API layer over the Stage 1 backbone.

## Development Status

The repository is currently in the Stage 1 planning and execution-harness phase.

The most important committed planning documents are:

- [Stage 1 backbone design (English)](docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design-en.md)
- [Stage 1 backbone design (Chinese)](docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design.md)
- [Stage 1 backbone implementation plan](docs/superpowers/plans/2026-04-20-qec-rd-stage1-backbone-implementation.md)
- [Three-person execution plan](docs/superpowers/plans/2026-04-21-qec-rd-stage1-3person-execution.md)
- [Workstream B plan](docs/superpowers/plans/2026-04-22-qec-rd-workstream-b-plan.md)
- [Agent workflow rules](AGENTS.md)
- [Repo working contract](CODEX.md)

## Collaboration Model

This project is being organized for multi-person parallel development.

The current execution harness assumes:

- shared Stage 1 scope and architecture are frozen before parallel coding
- work is split into focused workstreams with clear ownership
- contributors work through platform objects instead of bypassing the backbone
- tests and docs move together with each mergeable slice

## Team

- [shunzgim](https://github.com/shunzgim)
- [Chriskmh](https://github.com/Chriskmh)
- [LeiZhang-116-4](https://github.com/LeiZhang-116-4)

## Issues

Task tracking and discussion live in [GitHub Issues](https://github.com/QuAIR/QEC-RD-Software/issues).

## License

This project is licensed under the **Apache License 2.0**.

See [LICENSE](LICENSE) for the full text and [NOTICE](NOTICE) for attribution details.
