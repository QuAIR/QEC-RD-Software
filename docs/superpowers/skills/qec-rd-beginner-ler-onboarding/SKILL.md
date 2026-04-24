---
name: qec-rd-beginner-ler-onboarding
description: Use when a beginner needs to learn QEC-RD-Software through the guided demos and finish with one logical-error-rate experiment instead of jumping straight to the heavy acceptance showcase.
---

# QEC-RD Beginner LER Onboarding

## Overview

This skill teaches the repo in the same order as the guided demos.

Core principle: explain just enough to get a beginner to one successful `LER`
run, then stop before the workflow turns into a threshold or benchmarking task.

## When To Use

Use this skill when:

- A new user needs a first successful `LER` run
- The request mentions guided demos or beginner onboarding
- The goal is understanding `code`, `noise`, `decoder`, and `target`
- A reviewer asks for a beginner-friendly walkthrough instead of a full showcase

Do not use this skill to:

- Run the heavy acceptance showcase first
- Turn a first-contact walkthrough into a threshold study
- Replace the fixed Stage 1 acceptance demo

## Onboarding Flow

1. Start from the guided demo chain, not raw API internals
2. Explain the four beginner keywords in order:
   `code -> noise -> decoder -> target`
3. Map those keywords onto one simple `ExperimentConfig`
4. Run one `LER` experiment
5. Report the result in plain language

## Preferred Default Path

- `code`: `rotated_surface_code`
- `noise`: `si1000`
- `decoder`: `pymatching`
- `target`: `ler`

Use the quick default demo when possible:

```powershell
python -m qec_rd.demo
```

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Starting with threshold | Stop at one `LER` run first |
| Explaining QEC theory too deeply | Explain only the keywords needed for the run |
| Jumping to imported circuits | Keep imported circuits as supplementary material |
| Treating Demo 5 as the beginner path | Use Demo 5 only after the beginner path is understood |

## Stage 1 Guard

Keep the walkthrough inside Stage 1: `stim` backend only, fixed DEM/graph
behavior, external decoders, and no non-Pauli runtime claims.
