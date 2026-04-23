---
name: qec-rd-stage1-guardrails
description: Use when reviewing or implementing changes that might drift beyond the approved Stage 1 architecture or public boundaries in QEC-RD-Software.
---

# QEC-RD Stage 1 Guardrails

## Overview

This skill is a scope check for contributors and agents.

Core principle: protect the approved Stage 1 backbone from architecture drift while still allowing practical engineering progress.

## When To Use

Use this skill when:

- Reviewing a PR for Stage 1 scope compliance
- Deciding whether a new idea belongs in Stage 1 or a later stage
- Writing docs or tests that define public expectations
- Making changes near the public object chain or user customization boundaries

Do not use this skill when:

- The work is already an agreed Stage 2 topic
- The task is a small isolated bugfix entirely inside established Stage 1 behavior

## Stage 1 Non-Negotiables

- Runtime backend is `stim` only.
- Built-in catalog is repetition, rotated surface, unrotated surface, and toric.
- User customization is circuit import, decoder hooks, syndrome data input, and analysis hooks.
- Arbitrary custom code definitions are out of scope for the Stage 1 user interface.
- DEM and decoding graph behavior are fixed and platform-owned.
- Non-Pauli runtime noise is out of scope.
- Decoder algorithms come from external packages or custom hooks.

## Review Questions

Before accepting a change, ask:

1. Does this preserve the `CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport` chain?
2. Does it keep `stim` as the only runtime backend?
3. Does it avoid opening DEM or graph customization to users?
4. Does it avoid introducing non-Pauli runtime behavior?
5. Does it keep decoders external or hook-based instead of reimplemented in-repo?

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating every extension point as urgent | Keep only the agreed Stage 1 extension points. |
| Exposing backend-native objects in public docs | Speak in terms of platform objects first. |
| Sneaking Stage 2 topics into Stage 1 demos | Record them as future work instead. |

## Escalate When

Stop and ask before proceeding if a change needs:

- A new backend provider model
- User-customizable DEM or graph construction
- Non-Pauli runtime execution
- In-repo decoder reimplementation
- A materially different public object chain
