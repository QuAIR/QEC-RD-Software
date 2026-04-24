---
name: qec-rd-experiment-design
description: Use when a user goal or review task must be translated into a minimal QEC-RD-Software experiment configuration with sensible code, noise, decoder, and shot choices.
---

# QEC-RD Experiment Design

## Overview

This skill chooses a runnable experiment shape from an intent.

Core principle: pick the smallest experiment that answers the question without drifting beyond Stage 1.

## When To Use

Use this skill when:

- A user asks for “an experiment” but not exact parameters
- A review demo needs a stable default setup
- A research question needs to be converted into a first runnable config
- Multiple built-in paths are possible and one must be selected

Do not use this skill to:

- Present final reviewer output
- Deep-diagnose a suspicious result

## Design Flow

1. Identify the question: smoke test, comparison, decoder check, or noise check
2. Choose the smallest built-in family or imported circuit that answers it
3. Choose a Stim-executable noise model aligned with the goal
4. Choose the simplest decoder that is valid for the DEM structure
5. Pick a shot count just large enough for the claim being made

## Default Bias

Prefer:

- `repetition_code:memory` for first demos
- Built-in circuits before imported circuits
- MWPM before more complex decoder stories
- Small distances and modest shots for review runs

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Starting with the fanciest demo | Start with the most stable one |
| Using large-shot threshold runs for onboarding | Use a small, fast acceptance path first |
| Picking parameters without a success criterion | Tie each choice to the question being answered |

## Stage 1 Guard

Keep the design inside Stim-only runtime, built-in catalog plus circuit import, and fixed DEM/graph behavior.
