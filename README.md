# QEC-RD-Software

<p align="center">
  <img src="assets/logos/qec-rd-logo-primary.png" alt="QEC-RD logo" width="520">
</p>

[![CI](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/ci.yml/badge.svg)](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/ci.yml)
[![Coverage](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/coverage.yml/badge.svg)](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/coverage.yml)
[![Codecov](https://codecov.io/gh/QuAIR/QEC-RD-Software/branch/main/graph/badge.svg)](https://codecov.io/gh/QuAIR/QEC-RD-Software)
[![Docs Online](https://img.shields.io/badge/docs-online-blue)](https://quairkit.com/QEC-RD-Software/)
[![Generated Docs](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/docs.yml/badge.svg)](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/docs.yml)

QEC-RD-Software is a local research and engineering backbone for quantum error correction (QEC). It connects circuit construction, detector-error-model (DEM) extraction, syndrome sampling, decoding, and analysis behind a small Python API.

Stage 1 is intentionally focused: `stim` is the only runtime backend, DEM/graph logic is platform-owned, non-Pauli runtime noise is out of scope, and decoders come from external packages or custom decoder hooks.

Live documentation: [quairkit.com/QEC-RD-Software](https://quairkit.com/QEC-RD-Software/)

## Evaluation Prompt

```text
Read the QEC-RD beginner onboarding skill and follow it.
```

## Why This Repo Exists

Many QEC experiments start as separate scripts: one script builds a circuit, another extracts a DEM, another runs a decoder, and another analyzes logical failures. This project turns that workflow into a stable object chain:

`CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`

That object chain is the shared language for users, researchers, and future engineering contributors.

## Main Features

- Built-in circuit catalog for repetition, rotated surface, unrotated surface, and toric memory experiments.
- Circuit import path for user-provided `stim.Circuit` objects or `.stim` files.
- Fixed DEM extraction and decoding-graph construction owned by the platform.
- Stim-based syndrome sampling normalized into `SyndromeBatch`.
- Stim-executable Pauli-style noise presets, including toy, toy phenomenological, SD6, scheduled SI1000-style, and coarse circuit-level SI1000-style models.
- External MWPM decoding through `pymatching`.
- Custom decoder hooks that return the same `DecodeResult` shape.
- Analysis reports with logical error rate, failure counts, and per-logical summaries.

## Beginner Onboarding

If you are new to QEC-RD-Software, the beginner path is:

1. install the package
2. understand the four keywords used by this repo:
   `code`, `noise`, `decoder`, `target`
3. run one logical-error-rate (`LER`) experiment
4. only then look at the heavier acceptance showcase

The repo-local skill for that path is:

- [QEC-RD beginner onboarding skill](docs/superpowers/skills/qec-rd-beginner-ler-onboarding/SKILL.md)

## Install

From the repository root:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,docs]"
```

If you only want to run the package without docs tooling:

```powershell
python -m pip install -e ".[dev]"
```

## What You Can Choose In Stage 1

### Codes

Stage 1 has a built-in circuit catalog for:

- `repetition_code:memory`
- `rotated_surface_code`
- `unrotated_surface_code`
- `toric_code`

For beginners, the recommended first code is `rotated_surface_code`.

### Noise Models

Stage 1 keeps noise limited to Stim-executable Pauli-style presets:

- `toy`
- `toy_phenomenological`
- `sd6`
- `si1000`
- `stim_circuit_level_si1000`

For beginners, the recommended first noise preset is `si1000`.

### Decoders

Stage 1 supports external decoder adapters and custom hooks:

- `pymatching` for MWPM
- `bposd` through `ldpc`
- `custom` via `decoder_fn`

For beginners, the recommended first decoder is `pymatching`.

### Targets

For beginner usage, think in terms of two analysis targets:

- `ler`: one configured experiment returning a logical error rate
- `threshold`: a heavier multi-distance sweep

The beginner path should stop at one successful `LER` run.

## First Logical-Error-Rate Experiment

This is the recommended first successful run for a new user. It uses the four
beginner keywords in their default form:

- `code = rotated_surface_code`
- `noise = si1000`
- `decoder = pymatching`
- `target = ler`

### Quickest Path

From the repository root:

```powershell
python -m qec_rd.demo
```

If the editable install has been completed, the equivalent short command is:

```powershell
qec-rd-demo
```

This quick path runs:

- built-in `rotated_surface_code`
- scheduled `si1000` noise
- MWPM decoding through `pymatching`
- `1000` shots

### Plain-Language Meaning

The command above means:

- build a built-in rotated surface memory circuit
- inject one of the repo's Stage 1 noise presets
- extract the detector error model and decoding graph
- sample noisy syndrome data
- decode with MWPM
- report one logical error rate

### Equivalent API Example

This is the same beginner path through the public API:

```python
from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, run_experiment

config = ExperimentConfig(
    code_spec=CodeSpec(
        family="rotated_surface_code",
        distance=3,
        rounds=3,
        logical_basis="Z",
    ),
    noise_spec=NoiseModel.si1000(p=0.001),
    decoder_spec={"name": "pymatching"},
    sim_spec={"shots": 1000, "seed": 11},
)

result = run_experiment(config)

print(result.analysis_report.shot_count)
print(result.analysis_report.logical_error_rate)
```

After it finishes, a valid beginner outcome is simply:

- the run completes
- the shot count is reported
- the `logical_error_rate` is between `0.0` and `1.0`

## Acceptance Showcase

After the beginner `LER` path is understood, the fixed acceptance showcase is:

- `rotated_surface_code`
- distances `d = 3, 5, 7`
- scheduled `si1000`
- `pymatching` / MWPM
- `10000` shots per point

To regenerate it from the repository root:

```powershell
python -m qec_rd.showcase
```

Or, after editable install:

```powershell
qec-rd-showcase
```

The committed acceptance figure:

![Acceptance showcase](docs/assets/rotated_surface_si1000_threshold_showcase.png)

Raw data:

- [CSV](docs/assets/rotated_surface_si1000_threshold_showcase.csv)
- [JSON](docs/assets/rotated_surface_si1000_threshold_showcase.json)

Build the docs locally with:

```powershell
mkdocs build --strict
```

Documentation entry points in this repository:

- [Docs Home](docs/index.md)
- [API Reference](docs/api/index.md)

Latest generated documentation artifact:

- [Generated Docs workflow](https://github.com/QuAIR/QEC-RD-Software/actions/workflows/docs.yml)

The badge above now means the workflow successfully built the MkDocs site and uploaded it as a downloadable artifact. It is a generated documentation bundle, not a hosted GitHub Pages website.

## Public API Map

Most users should start from `qec_rd.api`:

```python
from qec_rd.api import (
    CodeSpec,
    ExperimentConfig,
    NoiseModel,
    build_circuit,
    extract_dem,
    build_decoding_graph,
    sample_syndromes,
    run_decoder,
    analyze_results,
    run_experiment,
    sweep,
)
```

The direct pipeline API is useful when you want to inspect each artifact. The runner API is useful when you want a compact experiment configuration.

## Development Workflow

Run the test suite:

```powershell
pytest -q
```

Run the coverage gate:

```powershell
pytest --cov=qec_rd --cov-report=term-missing --cov-report=xml -q
```

Build docs:

```powershell
mkdocs build --strict
```

The repository has three GitHub Actions workflows:

- `.github/workflows/ci.yml` for tests
- `.github/workflows/coverage.yml` for coverage report generation, artifact upload, and Codecov upload
- `.github/workflows/docs.yml` for MkDocs site generation and artifact upload

## Contributor Orientation

Before changing architecture or public behavior, read:

- [AGENTS.md](AGENTS.md) for agent and contributor rules
- [CODEX.md](CODEX.md) for the working contract
- [Stage 1 backbone design](docs/superpowers/specs/2026-04-20-qec-rd-platform-backbone-design-en.md)
- [Three-person execution plan](docs/superpowers/plans/2026-04-21-qec-rd-stage1-3person-execution.md)

Agent skills for common tasks:

- [Beginner onboarding](docs/superpowers/skills/qec-rd-beginner-ler-onboarding/SKILL.md)

Keep Stage 1 changes small and testable. Do not add non-Pauli runtime behavior, do not make DEM/graph construction user-customizable, and do not reimplement external decoders inside this repo.

## Current Limitations

- Runtime backend is `stim` only.
- Surface and toric circuits are platform-owned Stage 1 implementations.
- DEM and graph behavior are fixed in Stage 1.
- Non-Pauli noise and leakage are outside Stage 1 runtime scope.
- Coverage reports are uploaded to Codecov and available as workflow artifacts.

## Team

- [shunzgim](https://github.com/shunzgim)
- [Chriskmh](https://github.com/Chriskmh)
- [LeiZhang-116-4](https://github.com/LeiZhang-116-4)

## License

This project is licensed under the Apache License 2.0.

**Why Apache 2.0?**
- Permissive for academic research and commercial use alike.
- Compatible with the licenses of our key dependencies (`stim`, `pymatching`, `ldpc`, `numpy`, `scipy`).
- Patent grant clause protects contributors and downstream users.
- Standard choice in the quantum software ecosystem.

See [LICENSE](LICENSE) for the full text and [NOTICE](NOTICE) for attribution details.
