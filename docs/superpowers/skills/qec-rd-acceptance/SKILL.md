---
name: qec-rd-review-presentation
description: Use when a QEC-RD-Software run, demo, or milestone needs to be summarized for reviewers, collaborators, or acceptance discussion instead of dumped as raw logs.
---

# QEC-RD Review Presentation

## Overview

This skill turns a run into a reviewer-friendly story.

Core principle: present the smallest convincing narrative, not the largest amount of output.

## When To Use

Use this skill when:

- A demo has finished and needs a short review summary
- A reviewer needs to know what pipeline was exercised
- Results need to be framed as accepted, limited, or blocked
- Raw logs exist but are too noisy to hand over directly

Do not use this skill to:

- Choose the experiment itself
- Diagnose suspicious results in depth
- Add new requirements during presentation

## Presentation Flow

1. State what was run in one line
2. Name the exercised pipeline stages
3. Report the key numerical result
4. Call out known limitations honestly
5. End with a clear status: works, works with limitations, or needs follow-up

## Preferred Structure

- Demo or experiment name
- Pipeline exercised
- Key result
- Known limitation, if any
- Reviewer takeaway

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Copying raw terminal output | Summarize the evidence in reviewer language |
| Hiding limitations | State them explicitly and tie them to Stage 1 scope |
| Over-explaining internal details | Keep focus on what was exercised and what happened |

## Stage 1 Guard

Present results in terms of platform artifacts and pipeline stages, not backend implementation trivia.
