---
name: qec-rd-acceptance
description: Use when QEC-RD-Software is ready for a Stage or milestone acceptance check, release-readiness review, or human verification pass.
---

# QEC-RD Acceptance

## Overview

Acceptance is an evidence-gathering stage, not a feature-building stage.

Core principle: verify the project against the agreed Stage scope, record evidence, and clearly classify the result before declaring acceptance.

## When To Use

Use this skill when:

- The project or branch is believed to be ready for Stage acceptance.
- A human verification pass is requested.
- A milestone needs an accept / accept-with-limitations / reject decision.
- The team needs a reproducible acceptance report before merging or moving to the next stage.

Do not use this skill to:

- Add new architecture.
- Fix bugs discovered during acceptance.
- Expand Stage 1 scope.
- Run acceptance before the user explicitly asks for the acceptance check.

## Required Background

Use these supporting skills when their triggers apply:

- **REQUIRED:** `superpowers:verification-before-completion` before making any passing or completion claim.
- **RECOMMENDED:** `superpowers:requesting-code-review` before accepting major merged work.
- **OPTIONAL:** `superpowers:finishing-a-development-branch` when acceptance is complete and branch integration is needed.

## Stage 1 Scope Guard

Acceptance must check the project against the approved Stage 1 backbone:

- Runtime backend is `stim` only.
- Built-in circuit catalog includes repetition, rotated surface, unrotated surface, and toric targets.
- Surface and toric circuits are platform-owned, not generated through `stim.Circuit.generated`.
- User customization is through circuit import, decoder hooks, syndrome data input, and analysis hooks.
- Arbitrary user-defined code objects are not part of the Stage 1 user interface.
- Noise models are Stim-executable Pauli / measurement / reset / idle style models only.
- Non-Pauli runtime noise is out of scope.
- DEM and graph construction are platform-owned and not user-customizable.
- Decoders use external packages or custom decoder hooks, not in-repo decoder reimplementation.

## Acceptance Workflow

1. Create or switch to a dedicated acceptance branch from the current accepted base, usually `origin/main`.
2. Preserve unrelated local changes; do not include unfinished implementation work in the acceptance branch.
3. Read the current Stage specs, execution plans, `AGENTS.md`, `CODEX.md`, README, and the human verification issue.
4. Build an acceptance checklist from the agreed scope, not from new ideas discovered during review.
5. Run fresh automated verification and record command, exit code, and important output.
6. Run targeted end-to-end QEC checks and record input settings, observed behavior, and limitations.
7. Compare the evidence against the checklist line by line.
8. Produce an acceptance report with one of three outcomes: accepted, accepted with known limitations, or not accepted.
9. If bugs are found, stop acceptance and open a follow-up issue or fix branch; do not silently fix inside the acceptance pass.

## Minimum Evidence

The acceptance report should include:

- Git branch and commit SHA under review.
- Working tree status and whether unrelated local changes were excluded.
- Automated checks such as tests, coverage command, and docs build.
- Built-in circuit smoke checks for repetition, rotated surface, unrotated surface, and toric.
- Circuit import smoke check for at least one supported imported circuit format.
- Noise model smoke checks, including SI1000-style scheduled noise and simple phenomenological noise.
- DEM extraction and decoding graph checks.
- MWPM decoding check through `pymatching`.
- BP+OSD decoding check through `ldpc`, if the dependency is available.
- Custom decoder hook smoke check.
- Analysis report generation check.
- Known limitations and whether each is acceptable for the current Stage.

## QEC End-To-End Checks

At minimum, run small-shot checks before any larger benchmark:

- Built-in memory circuit generation for each catalog target.
- Noise injection with a Stim-executable noise model.
- DEM extraction from the noisy circuit.
- Syndrome sampling.
- Decode through MWPM.
- Generate an analysis report with logical error rate and shot counts.

Large threshold-style experiments are optional acceptance evidence unless explicitly requested.

## Report Format

Use this compact structure:

```markdown
# QEC-RD Acceptance Report

Branch:
Commit:
Date:
Reviewer:

## Outcome
Accepted / Accepted with known limitations / Not accepted

## Evidence
- Command: ...
- Result: ...

## Scope Checklist
- [ ] ...

## Known Limitations
- ...

## Follow-Up Issues
- ...
```

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating acceptance as debugging | Stop and open a fix branch or issue. |
| Saying "it should pass" | Run fresh verification and cite evidence. |
| Adding new requirements mid-check | Record as future work, not Stage acceptance scope. |
| Mixing dirty local work into acceptance | Isolate acceptance changes or report the dirty state clearly. |
| Accepting because CI is green only | Also run the QEC-specific end-to-end checks. |

## Red Flags

Stop and ask before proceeding if acceptance requires:

- Expanding Stage 1 beyond `stim`.
- Adding non-Pauli runtime behavior.
- Making DEM or graph construction customizable by users.
- Replacing external decoder packages with in-repo implementations.
- Accepting with failing tests.
- Silently fixing code inside the acceptance branch.
