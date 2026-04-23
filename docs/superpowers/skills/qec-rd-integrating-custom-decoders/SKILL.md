---
name: qec-rd-integrating-custom-decoders
description: Use when connecting a user-provided decoder to the QEC-RD-Software Stage 1 pipeline through the custom decoder hook.
---

# QEC-RD Integrating Custom Decoders

## Overview

Stage 1 allows custom decoders, but it does not allow custom DEM or graph construction.

Core principle: custom decoders plug into stable platform inputs and return a standard `DecodeResult`.

## When To Use

Use this skill when:

- Writing a custom decoder example
- Adapting an external decoder not yet wrapped by the repo
- Testing the custom decoder hook
- Documenting the expected custom decoder contract

Do not use this skill when:

- Reimplementing MWPM or BP+OSD inside the repo
- Exposing backend-native decoder internals as the public API

## Decoder Contract

Inputs:

- `DecodingGraph`
- `SyndromeBatch`
- Optional decoder-specific keyword arguments

Output:

- `DecodeResult`

If a helper decoder produces raw observable predictions, normalize them with `normalize_custom_decode_result`.

## Recommended Flow

1. Build or import a circuit
2. Extract DEM and build graph
3. Sample syndromes
4. Call `run_decoder(..., decoder_name="custom", decoder_fn=...)`
5. Analyze the returned `DecodeResult`

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Returning a dict or tuple from the custom decoder | Return a `DecodeResult` or normalize into one. |
| Mutating graph or batch objects in-place | Treat inputs as read-only experiment artifacts. |
| Using custom decoders to change DEM semantics | Keep DEM and graph logic platform-owned in Stage 1. |

## Minimum Verification

- Custom decoder runs through `run_decoder`
- Return value is a valid `DecodeResult`
- Failure mask length matches shot count
- The result can be passed to `analyze_results`
