---
name: qec-rd-beginner-ler-onboarding
description: Use when a beginner needs to learn QEC-RD-Software from the repository README and finish with one logical-error-rate experiment instead of jumping straight to the heavy acceptance showcase.
---

# QEC-RD Beginner LER Onboarding

## Overview

This skill treats `README.md` as the primary teaching entry point.

Core principle: explain just enough to get a beginner to one successful `LER`
run, then stop before the workflow turns into a threshold or benchmarking task.

## When To Use

Use this skill when:

- A new user needs a first successful `LER` run
- The request mentions beginner onboarding or the evaluation prompt
- The goal is understanding `code`, `noise`, `decoder`, and `target`
- A reviewer asks for a beginner-friendly walkthrough instead of a full showcase

Do not use this skill to:

- Run the heavy acceptance showcase first
- Turn a first-contact walkthrough into a threshold study
- Replace the fixed Stage 1 acceptance demo

## Onboarding Flow

1. Read `README.md` first
2. Present the repo's main features in beginner-friendly language
3. Explain the four beginner keywords in order:
   `code -> noise -> decoder -> target`
4. Map those keywords onto one simple `ExperimentConfig`
5. Run one `LER` experiment
6. Report the result in plain language

Do not require the user to read the old demo pages as the default path.

## README-First Focus

Use the README to teach:

- what the package can do
- which built-in codes exist
- which Stage 1 noise models exist
- which decoders and targets exist
- the recommended first `LER` path
- where the fixed acceptance showcase lives

## Preferred Default Path

Use the README's beginner path whenever possible:

1. install `.[dev]` or `.[dev,docs]`
2. Explain the four beginner keywords in order:
   - `code`: `rotated_surface_code`
   - `noise`: `si1000`
   - `decoder`: `pymatching`
   - `target`: `ler`
3. Use the quick default demo when possible:

   ```powershell
   python -m qec_rd.demo
   ```

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Starting from API details | Start from the README summary and beginner path |
| Starting with threshold | Stop at one `LER` run first |
| Explaining QEC theory too deeply | Explain only the keywords needed for the run |
| Jumping to imported circuits first | Keep imported circuits as supplementary material |
| Treating the acceptance showcase as the beginner path | Use the fixed showcase only after the beginner path is understood |

## Stage 1 Guard

Keep the walkthrough inside Stage 1: `stim` backend only, fixed DEM/graph
behavior, external decoders, and no non-Pauli runtime claims.
