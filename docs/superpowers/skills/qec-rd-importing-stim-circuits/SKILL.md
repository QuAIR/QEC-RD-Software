---
name: qec-rd-importing-stim-circuits
description: Use when validating or documenting circuit import in QEC-RD-Software through a stim.Circuit object or .stim file.
---

# QEC-RD Importing Stim Circuits

## Overview

Circuit import is the main Stage 1 customization path for users.

Core principle: let users customize the circuit input while keeping DEM extraction, graph construction, decoding, and analysis platform-owned.

## When To Use

Use this skill when:

- Loading a `stim.Circuit` directly
- Loading a `.stim` file from disk
- Writing docs or tests around imported-circuit workflows
- Comparing generated and imported circuits through the same downstream pipeline

Do not use this skill when:

- Designing a custom code-definition interface
- Accepting arbitrary non-Stim formats as Stage 1 runtime inputs

## Allowed Stage 1 Inputs

- `stim.Circuit`
- `.stim` files

Future formats may be added later, but Stage 1 should describe imported circuits in terms of `CircuitArtifact`, not backend-native file handling.

## Standard Flow

1. Load the source with `load_circuit`
2. Confirm `CircuitArtifact.source_kind`
3. Extract DEM
4. Build decoding graph
5. Sample and decode
6. Produce an analysis report

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating imported circuits as a separate analysis path | Reuse the same DEM, graph, decode, and analysis flow. |
| Accepting unsupported suffixes silently | Raise an explicit unsupported-format error. |
| Letting imported circuits bypass platform objects | Always wrap them in `CircuitArtifact`. |

## Minimum Verification

- Imported circuit is wrapped as `CircuitArtifact`
- `source_kind` matches object or file import
- DEM extraction succeeds
- A decoder can run on sampled syndromes
- The final report includes shot count and logical error rate
