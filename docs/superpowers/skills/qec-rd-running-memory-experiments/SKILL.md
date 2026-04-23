---
name: qec-rd-running-memory-experiments
description: Use when running or documenting a Stage 1 built-in memory experiment in QEC-RD-Software from circuit generation through decoding and analysis.
---

# QEC-RD Running Memory Experiments

## Overview

This skill is for the standard Stage 1 experiment path on built-in codes.

Core principle: run the full platform chain and keep the user-facing story centered on artifacts and reports, not backend internals.

## When To Use

Use this skill when:

- Running a repetition, rotated surface, unrotated surface, or toric memory experiment
- Writing a demo, smoke check, or acceptance example for built-in circuits
- Verifying that the direct pipeline API and runner API agree on the same experiment path

Do not use this skill when:

- Importing an external circuit file
- Adding a new decoder integration
- Proposing new Stage 1 code families

## Stage 1 Scope Guard

- Backend is `stim` only.
- Built-in memory targets are repetition, rotated surface, unrotated surface, and toric.
- Surface and toric circuits must be platform-owned.
- Noise must be Stim-executable and Pauli-like.

## Standard Flow

1. Build `CodeSpec`
2. Build or select `NoiseModel`
3. Construct `CircuitArtifact`
4. Extract `DemArtifact`
5. Build `DecodingGraph`
6. Sample `SyndromeBatch`
7. Decode into `DecodeResult`
8. Summarize with `AnalysisReport`

## Preferred APIs

Use the direct pipeline when inspecting intermediate artifacts:

```python
build_circuit -> extract_dem -> build_decoding_graph -> sample_syndromes -> run_decoder -> analyze_results
```

Use the runner API when the experiment is configuration-driven:

```python
run_experiment
sweep
run_until_failures
```

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Talking only about raw Stim objects | Report platform artifacts and final analysis. |
| Using non-built-in families in Stage 1 demos | Stay inside the approved built-in catalog. |
| Calling the experiment complete without decoding | Include the full pipeline through `AnalysisReport`. |

## Minimum Verification

- Circuit builds successfully
- DEM extraction succeeds
- Decoding graph has detectors and edges
- Syndrome batch has the requested shot count
- Decoder returns a `DecodeResult`
- Analysis report exposes shot count and logical error rate
