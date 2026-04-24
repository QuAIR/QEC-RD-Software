---
name: qec-rd-demo-selection
description: Use when several demos or workflow paths are possible and an agent must choose the best one for review, onboarding, or a fast end-to-end proof.
---

# QEC-RD Demo Selection

## Overview

This skill helps an agent choose the right demo, not merely run one.

Core principle: optimize for reviewer success rate first, breadth second.

## When To Use

Use this skill when:

- A reviewer asks for “one demo”
- The repo contains multiple valid end-to-end examples
- Time is limited and the safest path must be chosen
- A fresh agent needs a single recommended entry point

Do not use this skill to:

- Design a new experiment from scratch
- Explain suspicious results after execution

## Selection Heuristics

Choose the path that is, in order:

1. Most stable under Stage 1 assumptions
2. Fastest to run from repo root
3. Least dependent on optional setup
4. Most representative of the core pipeline

## Preferred Order

1. Official default demo
2. Built-in repetition memory demo
3. Other built-in memory demos
4. Imported-circuit or custom-decoder demos

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Choosing the most impressive demo first | Choose the most reliable first |
| Treating all demos as equal | Rank by setup friction and failure risk |
| Forcing custom-input paths in first contact | Prefer built-in paths unless import is the point |

## Stage 1 Guard

If a demo depends on non-Stage-1 ideas, it is not the default review choice.
