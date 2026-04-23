# AGENTS.md

## Purpose

This file explains how agents should work inside `QEC-RD-Software`.

It is aimed at:

- Codex agents
- delegated subagents
- future human contributors using the same workflow conventions

## Default Agent Mission

When working in this repository, agents should optimize for:

- preserving the approved Stage 1 backbone direction
- making small, testable, reviewable changes
- keeping code and docs aligned
- avoiding speculative architecture drift

## Required Behavior

### 1. Respect Stage 1 boundaries

Agents must assume the following unless explicitly told otherwise:

- backend is only `stim`
- built-in circuit-catalog targets include repetition, rotated surface, unrotated surface, and toric
- never use `stim.Circuit.generated(...)` as the implementation path for rotated surface, unrotated surface, or toric built-ins
- built-in surface and toric families must be platform-owned code objects plus platform-owned circuit construction
- repetition code is the only family where `stim.Circuit.generated(...)` may be tolerated for compatibility, but platform-owned objects are still preferred
- user-facing customization happens through circuit import and downstream analysis/decoder hooks, not arbitrary code-definition input
- Stage 1 should expose both the direct pipeline API and a DeltaKit-style runner API
- non-Pauli noise is out of scope
- DEM / graph behavior is fixed and platform-owned
- decoders come from external packages or custom decoder hooks

### 2. Work through platform objects

Agents should prefer the platform object chain:

- `CodeSpec`
- `CircuitArtifact`
- `DemArtifact`
- `DecodingGraph`
- `SyndromeBatch`
- `DecodeResult`
- `AnalysisReport`

Do not turn backend-native objects into the repo's public interface.

### 3. Keep tasks narrow

Each agent task should ideally own one clear responsibility, such as:

- object model
- code generation
- experiment runner orchestration
- DEM / graph path
- MWPM adapter
- BP+OSD adapter
- custom decoder hook
- analysis
- tests
- docs sync

### 4. Prefer tests with each change

Agents should add or update tests alongside implementation whenever feasible.

Minimum expectation:

- no non-trivial behavior change without verification
- no decoder integration without adapter tests
- no backbone-wide claims without at least one end-to-end path checked

## Recommended Delegation Boundaries

These are good task slices for separate agents:

- `core` model and type work
- built-in circuit catalog generation
- experiment runner orchestration
- circuit import support
- DEM extraction and fixed graph construction
- MWPM integration via `pymatching`
- BP+OSD integration via `ldpc`
- custom decoder hook
- analysis and reporting
- test hardening

These are poor delegation slices:

- "implement everything in Stage 1"
- "refactor the whole repo first"
- "add all possible future extension points"

## Review Standards

Before a task is considered done, the agent should check:

- does it match the Stage 1 spec?
- does it stay inside Stage 1 scope?
- does it avoid adding non-Pauli behavior?
- does it avoid opening DEM/graph customization?
- does it preserve the end-to-end backbone flow?
- are tests or verification steps included?

## Documentation Rules

If a change affects repo-wide behavior, agents should update the relevant docs:

- spec files in `docs/superpowers/specs/`
- plan files in `docs/superpowers/plans/`
- `CODEX.md`
- `AGENTS.md`

## Branch and Task Hygiene

When using isolated branches or worktrees:

- prefer one task or one focused batch per branch
- keep commits readable and scoped
- avoid mixing unrelated architecture changes into one patch

When not using worktrees:

- stay even stricter about task scoping

## Escalation Triggers

Agents should stop and ask before proceeding if they discover a need to:

- expand Stage 1 to non-Pauli runtime behavior
- make DEM / graph logic user-customizable
- introduce a plugin/provider framework
- change the agreed built-in circuit-catalog scope
- replace external decoder packages with in-repo implementations
- change the public object chain materially

## Short Version

Agents in this repo should:

- implement the Stage 1 backbone, not reinvent the roadmap
- keep `stim` as the only runtime backend
- support built-in repetition/surface/toric circuit generation plus imported circuits
- keep built-in surface/toric generation platform-owned instead of routing through `stim.Circuit.generated(...)`
- use external decoder packages
- keep DEM / graph logic fixed in Stage 1
- preserve end-to-end flow
- keep tests and docs in sync
