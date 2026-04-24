# QEC-RD README-First Acceptance Entry Design

Date: 2026-04-24

## Goal

Turn the repository acceptance experience into a single-entry onboarding path:

- `README.md` becomes the primary and sufficient entry point for a new user
- the existing demo teaching content is folded into `README.md`
- the acceptance agent should rely on the existing onboarding skill, updated to read the README
- the final one-line evaluation prompt should tell the agent to read that skill

This design is specifically for the project submission and final review flow.

## Approved Direction

Use a `README-first` structure instead of a `README + demos` structure.

That means:

- `docs/demos/` is no longer the main onboarding surface
- beginner teaching content moves into `README.md`
- the existing onboarding skill becomes the agent-facing execution contract
- the prompt becomes the reviewer-facing trigger

## User Experience Target

A complete beginner should be able to hand the repository to a fresh agent and
use a one-line prompt that effectively means:

1. read the onboarding skill
2. use the README as the primary source of truth
3. install what is needed
4. explain what the package can do
5. teach the beginner how to run one logical-error-rate experiment
6. optionally point to the fixed acceptance showcase

The beginner should not need to open several demo pages to understand the repo.

## Content Restructure

The current demo teaching material is reorganized into `README.md` sections:

1. What this repository does
2. Supported built-in codes
3. Supported Stage 1 noise models
4. Supported decoders and analysis targets
5. Beginner path: one logical-error-rate experiment
6. Acceptance path: fixed rotated-surface showcase

The imported circuit example may remain as supplementary reference material, but
it should no longer be the main beginner path.

## Role Of The Skill

The existing onboarding skill should be the execution layer for agents, not a duplicate manual.

Its job is to tell the agent:

- read `README.md` first
- present the main features in beginner-friendly language
- install dependencies if needed
- follow the README's beginner path
- stop at one successful `LER` run unless the user explicitly asks for more
- treat the fixed showcase as the advanced acceptance result, not the first step

The skill should not require reading the old demo pages as part of the default
flow.

## Role Of The Prompt

The prompt should be reduced to a one-line trigger such as:

`Read the QEC-RD beginner onboarding skill and follow it.`

That keeps the prompt small while moving the real behavior contract into the
repo-local skill.

## Documentation Changes

Planned documentation changes:

- rewrite `README.md` as the single teaching entry point
- remove `docs/demos/` pages from the main onboarding path
- update `mkdocs.yml` to stop advertising demo pages as the primary sequence
- update the skills index and contributor-facing links to point at the new skill

## Acceptance Criteria

This redesign is successful when:

- a new agent can rely on the README alone for beginner onboarding
- the one-line prompt points to a skill, not a long instruction block
- the README directly teaches a beginner enough to run one `LER` experiment
- the fixed acceptance showcase remains available as the advanced final result
- the repo no longer depends on the old demo sequence to explain basic usage

## Non-Goals

- changing the Stage 1 technical scope
- replacing the fixed acceptance showcase
- adding free-form natural-language experiment parsing
- turning the beginner path into a threshold study
