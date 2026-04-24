---
name: qec-rd-beginner-onboard
description: Use when a beginner needs to learn QEC-RD-Software by following the repository README, completing installation, seeing the package features, and finishing with one logical-error-rate experiment before looking at the heavier acceptance showcase.
---

# QEC-RD Beginner Onboard

## Overview

This skill uses `README.md` as the live teaching script.

Core principle: show the README, teach from the README, and get a beginner to
one successful `LER` run before moving on.

Repository URL: `https://github.com/QuAIR/QEC-RD-Software`

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
7. Teach the user how to read the result
8. Only after that, point to the fixed acceptance showcase

## Required Teaching Output

Do not answer with a short task-completion summary.

The response must teach, not merely report. At minimum it should contain:

1. `What this repo does`
   Explain the package purpose using the README structure, not raw internals only.
2. `Beginner path`
   Tell the user exactly which command to run and why that path is the recommended first step.
3. `Run and result`
   Show the executed beginner path and explain what the reported `shots`,
   `logical_error_rate`, and `failure_count` mean in plain language.
4. `Acceptance figure`
   Show the fixed showcase image and explain why it is the advanced next step.

## Required Visual

When pointing to the acceptance showcase, embed this image directly in the
response instead of only mentioning it:

`![Acceptance showcase](D:/My_Code_Data_Desk/QEC-RD-Software/docs/assets/rotated_surface_si1000_threshold_showcase.png)`

## Required Commands

The teaching response should explicitly surface the beginner commands when used:

```powershell
python -m pip install -e ".[dev]"
python -m qec_rd.demo
```

If docs tooling is needed, also mention:

```powershell
python -m pip install -e ".[dev,docs]"
```

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

Explain why this is the default first contact:

- it uses the built-in rotated surface path
- it uses the recommended noise preset
- it uses the most standard decoder path
- it returns one `LER` result without turning into a heavy sweep

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Skipping the README | Use the README as the teaching script |
| Returning only a short completion summary | Teach the user in sections and explain the meaning of the result |
| Jumping to API details first | Start from the beginner sections in the README |
| Starting with threshold | Stop at one successful `LER` run first |
| Mentioning the acceptance showcase without showing it | Embed the fixed showcase image directly |
| Treating the acceptance showcase as the first demo | Keep it as the advanced final step |

## Guardrails

Keep the walkthrough inside the current platform boundaries: `stim` runtime,
fixed DEM/graph behavior, external decoders, and no non-Pauli runtime claims.
