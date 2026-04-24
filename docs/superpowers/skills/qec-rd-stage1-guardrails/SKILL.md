---
name: qec-rd-result-sanity-check
description: Use when a QEC-RD-Software result looks surprising and an agent must decide whether it reflects expected statistics, a known Stage 1 limitation, bad configuration, or a likely bug.
---

# QEC-RD Result Sanity Check

## Overview

This skill helps separate “interesting result” from “broken run”.

Core principle: classify the surprise before proposing a fix.

## When To Use

Use this skill when:

- A logical error rate looks implausible
- A decoder succeeds or fails unexpectedly
- A demo output needs a credibility check before presentation
- A reviewer asks whether a result is trustworthy

Do not use this skill to:

- Design the initial experiment
- Present final reviewer-facing prose before the result is classified

## Sanity Check Flow

1. Check whether the run stayed inside approved Stage 1 scope
2. Check whether the chosen decoder matches the DEM structure
3. Check whether shot count is large enough for the claim being made
4. Compare the result against known limitations and expected qualitative behavior
5. Classify the outcome as expected, limited, misconfigured, or likely buggy

## Classification Targets

- Expected statistical behavior
- Known Stage 1 architectural limitation
- Configuration or usage issue
- Implementation bug candidate

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating every odd result as a code bug | First check limitation and configuration buckets |
| Presenting untrusted numbers confidently | Classify the result before summarizing it |
| Ignoring Stage 1 boundaries during diagnosis | Use the agreed scope as the first filter |

## Stage 1 Guard

Known limits involving graphlike decoding, fixed DEM behavior, and Stim-only execution should be identified as scope constraints before escalating to bug claims.
