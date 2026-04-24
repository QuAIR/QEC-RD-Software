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
Run one complete end-to-end demo for this repo from the repo root, installing dependencies if needed.
Verify it works and briefly summarize the pipeline exercised and the result.
```

## Official Default Demo

From the repository root, the default evaluation path is:

```powershell
python -m qec_rd.demo
```

If the editable install has been completed, the equivalent short command is:

```powershell
qec-rd-demo
```

The default evaluation demo uses `rotated_surface_code` with scheduled SI1000-style noise, MWPM decoding through `pymatching`, and `1000` shots.

## Acceptance Showcase

For a heavier acceptance-oriented sweep that compares `MWPM` and `BP+OSD-0`
over `d = 3, 5, 7, 9` with scheduled `si1000`, use:

```powershell
python -m qec_rd.showcase
```

Or, after editable install:

```powershell
qec-rd-showcase
```

This generator writes `csv/json/png` assets into `docs/demos/assets/`.
It is intentionally slower than the quick default demo and is meant for
producing the final acceptance-style figure rather than first-contact onboarding.

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

## First Experiment

This runs a complete built-in repetition-code memory experiment with MWPM decoding:

```python
from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, run_experiment

config = ExperimentConfig(
    code_spec=CodeSpec(
        family="repetition_code:memory",
        distance=3,
        rounds=3,
        logical_basis="Z",
    ),
    noise_spec=NoiseModel(after_clifford_depolarization=0.001),
    decoder_spec={"name": "pymatching"},
    sim_spec={"shots": 100, "seed": 7},
)

result = run_experiment(config)

print(result.analysis_report.shot_count)
print(result.analysis_report.logical_error_rate)
```

## End-to-End Demos

The docs include five acceptance demos that validate the design:

- [Built-in repetition memory experiment](docs/demos/builtin-repetition-memory.md)
- [Rotated surface memory with scheduled SI1000-style noise](docs/demos/rotated-surface-si1000.md)
- [Imported Stim circuit pipeline](docs/demos/imported-stim-circuit.md)
- [Custom decoder hook](docs/demos/custom-decoder-hook.md)
- [Parameter sweep and analysis report](docs/demos/sweep-analysis-report.md)
- [Acceptance showcase generator](docs/demos/acceptance-showcase.md)

Build the docs locally with:

```powershell
mkdocs build --strict
```

Documentation entry points in this repository:

- [Docs Home](docs/index.md)
- [End-to-End Demos](docs/demos/index.md)
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

- [Acceptance testing](docs/superpowers/skills/qec-rd-acceptance/SKILL.md)
- [Importing Stim circuits](docs/superpowers/skills/qec-rd-importing-stim-circuits/SKILL.md)
- [Integrating custom decoders](docs/superpowers/skills/qec-rd-integrating-custom-decoders/SKILL.md)
- [Running memory experiments](docs/superpowers/skills/qec-rd-running-memory-experiments/SKILL.md)
- [Stage 1 guardrails](docs/superpowers/skills/qec-rd-stage1-guardrails/SKILL.md)

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
