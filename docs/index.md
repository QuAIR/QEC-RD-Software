# QEC-RD-Software Documentation

QEC-RD-Software is a Stage 1 quantum error correction research and engineering backbone.

The current platform focuses on a Stim-based workflow:

- built-in circuit catalog generation for repetition, rotated surface, unrotated surface, and toric codes
- circuit import as the main customization path
- fixed detector-error-model extraction and decoding graph construction
- syndrome sampling through Stim
- external decoder integration and custom decoder hooks
- analysis reports for logical error rate experiments

## Current Scope

Stage 1 intentionally stays narrow:

- Stim is the only runtime backend.
- Non-Pauli runtime behavior is out of scope.
- DEM and graph behavior are platform-owned.
- Decoder algorithms come from external packages or user-provided hooks.

## Start Here

Use the Stage 1 backbone specs and execution plans in this documentation site to understand the architecture, current boundaries, and collaboration model.
