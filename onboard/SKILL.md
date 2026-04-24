---
name: qec-rd-beginner-onboard
description: Use when a beginner needs to learn QEC-RD-Software by following the repository README, completing installation, seeing the package features, and finishing with one logical-error-rate experiment before looking at the heavier acceptance showcase.
---

# QEC-RD Beginner Onboard

## Overview

This skill uses `README.md` as the live teaching script.

Core principle: show the README, follow its structure, and get a beginner to
one successful `LER` run before moving on.

## When To Use

Use this skill when:

- A new user needs a first successful `LER` run
- The request mentions onboarding, getting started, or the evaluation prompt
- A reviewer wants a beginner-friendly walkthrough
- The task is to install the package, show what it can do, and teach one run

Do not use this skill to:

- Start with the heavier acceptance showcase
- Turn first-contact onboarding into a threshold study
- Replace the README with ad hoc explanations

## Onboarding Flow

1. Read `README.md` first
2. Show the README structure to the user in plain language
3. Present the package features directly from the README
4. Complete installation if needed
5. Explain the four beginner keywords:
   `code -> noise -> decoder -> target`
6. Follow the README's beginner `LER` path
7. Report the result briefly
8. Only after that, point to the fixed acceptance showcase

## Preferred Path

Use the README's default beginner route:

- `code`: `rotated_surface_code`
- `noise`: `si1000`
- `decoder`: `pymatching`
- `target`: `ler`

Use the quick path when possible:

```powershell
python -m qec_rd.demo
```

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Skipping the README | Use the README as the teaching script |
| Jumping to API details first | Start from the beginner sections in the README |
| Starting with threshold | Stop at one successful `LER` run first |
| Treating the acceptance showcase as the first demo | Keep it as the advanced final step |

## Guardrails

Keep the walkthrough inside the current platform boundaries: `stim` runtime,
fixed DEM/graph behavior, external decoders, and no non-Pauli runtime claims.
