---
name: qec-rd-decoder-choice
description: Use when an agent must decide which decoder path best fits a QEC-RD-Software experiment, given DEM structure, Stage 1 limits, and review goals.
---

# QEC-RD Decoder Choice

## Overview

This skill is about choosing the right decoder story for the task.

Core principle: choose the simplest decoder that is valid for the graph and the claim.

## When To Use

Use this skill when:

- A run could use MWPM, BP+OSD, or a custom decoder hook
- A demo needs the safest decoder for acceptance
- Graphlike versus hypergraph behavior matters
- A reviewer asks why one decoder was used over another

Do not use this skill to:

- Reimplement a decoder
- Change DEM semantics to force decoder compatibility

## Choice Rules

1. Prefer `pymatching` for graphlike Stage 1 acceptance paths
2. Use `ldpc` / BP+OSD when the goal is decoder breadth rather than the safest default demo
3. Use custom decoder hooks only when the task is explicitly about extension points
4. Escalate when the DEM structure exceeds the intended decoder assumptions

## Explanation Pattern

When reporting the choice, state:

- what the DEM structure permits
- why the selected decoder is the best fit
- what limitation is being accepted, if any

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating decoder choice as arbitrary | Tie it to graph structure and task goal |
| Defaulting to custom decoders for first demos | Keep first demos on external standard decoders |
| Hiding graphlike limitations | State them clearly when they affect the choice |

## Stage 1 Guard

Decoder choice must stay within external-package decoders or the custom hook, without reopening DEM or graph construction.
