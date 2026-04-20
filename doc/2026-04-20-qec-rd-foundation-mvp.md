# QEC R&D Foundation MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first usable vertical slice of the QEC R&D platform: Stim-backed circuit generation, configurable Pauli-noise injection, DEM export, baseline PyMatching decoding, and experiment reporting from a CLI.

**Architecture:** Use a narrow Python package centered on a small internal IR instead of exposing Stim primitives directly to every module. Keep the MVP strictly in the stabilizer / Pauli-noise regime so the platform has a clean, testable baseline before adding tensor-network simulation, coherent noise, or hardware calibration adapters in later plans.

**Tech Stack:** Python 3.11+, `stim`, `pymatching`, `sinter`, `typer`, `pytest`, `pandas`

---

## Scope Split

This project description covers multiple independent subsystems and should not be implemented as one giant plan. This plan covers only the **Foundation MVP**:

- Stim-backed code/circuit generation
- Pauli-style noise profile definition
- DEM extraction
- PyMatching baseline decoding
- CLI experiment runner and CSV/Markdown reporting

These items need separate follow-on plans after the MVP lands:

1. **Tensor / coherent-noise simulation plan**
2. **Advanced decoder plan** for BP/OSD, union-find, tensor decoders, custom heuristics
3. **Hardware calibration + real-device noise ingestion plan**
4. **FTQC resource estimation and scheduling plan**
5. **Control-instruction / DeltaKit-style lowering plan**

## Planned File Structure

### Package Files

- Create: `pyproject.toml`
- Create: `src/qec_rd/__init__.py`
- Create: `src/qec_rd/specs.py`
- Create: `src/qec_rd/circuit_generation.py`
- Create: `src/qec_rd/noise.py`
- Create: `src/qec_rd/dem.py`
- Create: `src/qec_rd/decoders/__init__.py`
- Create: `src/qec_rd/decoders/base.py`
- Create: `src/qec_rd/decoders/pymatching_decoder.py`
- Create: `src/qec_rd/experiments.py`
- Create: `src/qec_rd/reporting.py`
- Create: `src/qec_rd/cli.py`

### Tests

- Create: `tests/test_package_smoke.py`
- Create: `tests/test_circuit_generation.py`
- Create: `tests/test_noise_and_dem.py`
- Create: `tests/test_pymatching_decoder.py`
- Create: `tests/test_cli_experiment.py`

### Docs

- Create: `docs/architecture/foundation-mvp.md`

## Task 1: Bootstrap the Python package and test harness

**Files:**
- Create: `pyproject.toml`
- Create: `src/qec_rd/__init__.py`
- Create: `src/qec_rd/cli.py`
- Test: `tests/test_package_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
# tests/test_package_smoke.py
from typer.testing import CliRunner

from qec_rd.cli import app


def test_cli_help_shows_root_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "run-experiment" in result.stdout
    assert "QEC R&D" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_package_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'qec_rd'`

- [ ] **Step 3: Write the minimal package bootstrap**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "qec-rd"
version = "0.1.0"
description = "Foundation MVP for a QEC R&D workflow platform"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "pandas>=2.2",
  "pymatching>=2.2",
  "sinter>=1.14",
  "stim>=1.14",
  "typer>=0.12",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[project.scripts]
qec-rd = "qec_rd.cli:app"
```

```python
# src/qec_rd/__init__.py
__all__ = ["__version__"]

__version__ = "0.1.0"
```

```python
# src/qec_rd/cli.py
import typer

app = typer.Typer(
    help="QEC R&D foundation CLI for circuit generation, decoding, and analysis."
)


@app.command("run-experiment")
def run_experiment_placeholder() -> None:
    """Temporary placeholder command replaced in later tasks."""
    typer.echo("QEC R&D foundation CLI")


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_package_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/qec_rd/__init__.py src/qec_rd/cli.py tests/test_package_smoke.py
git commit -m "feat: bootstrap qec foundation package"
```

## Task 2: Add experiment specs and Stim-backed circuit generation

**Files:**
- Create: `src/qec_rd/specs.py`
- Create: `src/qec_rd/circuit_generation.py`
- Test: `tests/test_circuit_generation.py`

- [ ] **Step 1: Write the failing circuit-generation tests**

```python
# tests/test_circuit_generation.py
from qec_rd.circuit_generation import build_circuit
from qec_rd.specs import CircuitSpec


def test_build_repetition_memory_circuit() -> None:
    spec = CircuitSpec(
        code_family="repetition_memory",
        distance=3,
        rounds=3,
        logical_basis="x",
    )

    circuit = build_circuit(spec)

    assert circuit.num_qubits > 0
    assert circuit.num_detectors > 0


def test_build_rotated_surface_memory_circuit() -> None:
    spec = CircuitSpec(
        code_family="surface_code_rotated_memory",
        distance=3,
        rounds=3,
        logical_basis="z",
    )

    circuit = build_circuit(spec)

    assert circuit.num_qubits > 0
    assert circuit.num_observables >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_circuit_generation.py -v`
Expected: FAIL with `ImportError` for `qec_rd.circuit_generation` or missing `CircuitSpec`

- [ ] **Step 3: Write the circuit spec and generator**

```python
# src/qec_rd/specs.py
from dataclasses import dataclass
from typing import Literal


CodeFamily = Literal["repetition_memory", "surface_code_rotated_memory"]
LogicalBasis = Literal["x", "z"]


@dataclass(frozen=True)
class CircuitSpec:
    code_family: CodeFamily
    distance: int
    rounds: int
    logical_basis: LogicalBasis

    def validate(self) -> None:
        if self.distance < 3 or self.distance % 2 == 0:
            raise ValueError("distance must be an odd integer >= 3")
        if self.rounds < 1:
            raise ValueError("rounds must be >= 1")
```

```python
# src/qec_rd/circuit_generation.py
import stim

from qec_rd.specs import CircuitSpec


def build_circuit(spec: CircuitSpec) -> stim.Circuit:
    spec.validate()

    if spec.code_family == "repetition_memory":
        task_name = (
            "repetition_code:memory"
            if spec.logical_basis == "z"
            else "repetition_code:memory"
        )
        return stim.Circuit.generated(
            task_name,
            distance=spec.distance,
            rounds=spec.rounds,
        )

    if spec.code_family == "surface_code_rotated_memory":
        task_name = (
            "surface_code:rotated_memory_x"
            if spec.logical_basis == "x"
            else "surface_code:rotated_memory_z"
        )
        return stim.Circuit.generated(
            task_name,
            distance=spec.distance,
            rounds=spec.rounds,
        )

    raise ValueError(f"unsupported code_family={spec.code_family}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_circuit_generation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/specs.py src/qec_rd/circuit_generation.py tests/test_circuit_generation.py
git commit -m "feat: add stim-backed circuit generation"
```

## Task 3: Add noise specifications and DEM extraction

**Files:**
- Modify: `src/qec_rd/specs.py`
- Create: `src/qec_rd/noise.py`
- Create: `src/qec_rd/dem.py`
- Test: `tests/test_noise_and_dem.py`

- [ ] **Step 1: Write the failing noise and DEM tests**

```python
# tests/test_noise_and_dem.py
from qec_rd.circuit_generation import build_circuit
from qec_rd.dem import build_detector_error_model
from qec_rd.noise import apply_noise
from qec_rd.specs import CircuitSpec, NoiseSpec


def test_apply_noise_changes_circuit_text() -> None:
    circuit = build_circuit(
        CircuitSpec(
            code_family="surface_code_rotated_memory",
            distance=3,
            rounds=3,
            logical_basis="z",
        )
    )
    noisy = apply_noise(
        circuit,
        NoiseSpec(
            after_clifford_depolarization=0.001,
            before_round_data_depolarization=0.002,
            before_measure_flip_probability=0.003,
            after_reset_flip_probability=0.004,
        ),
    )

    assert str(noisy) != str(circuit)


def test_build_detector_error_model_returns_dem() -> None:
    circuit = build_circuit(
        CircuitSpec(
            code_family="surface_code_rotated_memory",
            distance=3,
            rounds=3,
            logical_basis="z",
        )
    )
    noisy = apply_noise(circuit, NoiseSpec())
    dem = build_detector_error_model(noisy)

    assert dem.num_detectors > 0
    assert dem.num_errors > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_noise_and_dem.py -v`
Expected: FAIL with missing `NoiseSpec`, `apply_noise`, or `build_detector_error_model`

- [ ] **Step 3: Extend specs and implement noise / DEM modules**

```python
# src/qec_rd/specs.py
from dataclasses import dataclass
from typing import Literal


CodeFamily = Literal["repetition_memory", "surface_code_rotated_memory"]
LogicalBasis = Literal["x", "z"]


@dataclass(frozen=True)
class CircuitSpec:
    code_family: CodeFamily
    distance: int
    rounds: int
    logical_basis: LogicalBasis

    def validate(self) -> None:
        if self.distance < 3 or self.distance % 2 == 0:
            raise ValueError("distance must be an odd integer >= 3")
        if self.rounds < 1:
            raise ValueError("rounds must be >= 1")


@dataclass(frozen=True)
class NoiseSpec:
    after_clifford_depolarization: float = 0.001
    before_round_data_depolarization: float = 0.001
    before_measure_flip_probability: float = 0.001
    after_reset_flip_probability: float = 0.001

    def validate(self) -> None:
        for value in (
            self.after_clifford_depolarization,
            self.before_round_data_depolarization,
            self.before_measure_flip_probability,
            self.after_reset_flip_probability,
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError("noise probabilities must be in [0, 1]")
```

```python
# src/qec_rd/noise.py
import stim

from qec_rd.specs import NoiseSpec


def apply_noise(circuit: stim.Circuit, noise_spec: NoiseSpec) -> stim.Circuit:
    noise_spec.validate()
    return circuit.with_inlined_feedback().without_noise().copy()
```

```python
# src/qec_rd/dem.py
import stim


def build_detector_error_model(circuit: stim.Circuit) -> stim.DetectorErrorModel:
    return circuit.detector_error_model(
        decompose_errors=True,
        allow_gauge_detectors=False,
        approximate_disjoint_errors=False,
    )
```

- [ ] **Step 4: Replace the placeholder noise implementation with Stim-native noisy generation**

```python
# src/qec_rd/circuit_generation.py
import stim

from qec_rd.specs import CircuitSpec, NoiseSpec


def build_circuit(spec: CircuitSpec, noise: NoiseSpec | None = None) -> stim.Circuit:
    spec.validate()
    noise = noise or NoiseSpec(0.0, 0.0, 0.0, 0.0)

    if spec.code_family == "repetition_memory":
        task_name = "repetition_code:memory"
    elif spec.code_family == "surface_code_rotated_memory":
        task_name = (
            "surface_code:rotated_memory_x"
            if spec.logical_basis == "x"
            else "surface_code:rotated_memory_z"
        )
    else:
        raise ValueError(f"unsupported code_family={spec.code_family}")

    return stim.Circuit.generated(
        task_name,
        distance=spec.distance,
        rounds=spec.rounds,
        after_clifford_depolarization=noise.after_clifford_depolarization,
        before_round_data_depolarization=noise.before_round_data_depolarization,
        before_measure_flip_probability=noise.before_measure_flip_probability,
        after_reset_flip_probability=noise.after_reset_flip_probability,
    )
```

```python
# src/qec_rd/noise.py
import stim

from qec_rd.specs import CircuitSpec, NoiseSpec


def apply_noise(spec: CircuitSpec, noise_spec: NoiseSpec) -> stim.Circuit:
    from qec_rd.circuit_generation import build_circuit

    noise_spec.validate()
    return build_circuit(spec, noise=noise_spec)
```

```python
# tests/test_noise_and_dem.py
from qec_rd.dem import build_detector_error_model
from qec_rd.noise import apply_noise
from qec_rd.specs import CircuitSpec, NoiseSpec


def test_apply_noise_changes_circuit_text() -> None:
    spec = CircuitSpec(
        code_family="surface_code_rotated_memory",
        distance=3,
        rounds=3,
        logical_basis="z",
    )
    clean = apply_noise(spec, NoiseSpec(0.0, 0.0, 0.0, 0.0))
    noisy = apply_noise(
        spec,
        NoiseSpec(
            after_clifford_depolarization=0.001,
            before_round_data_depolarization=0.002,
            before_measure_flip_probability=0.003,
            after_reset_flip_probability=0.004,
        ),
    )

    assert str(noisy) != str(clean)


def test_build_detector_error_model_returns_dem() -> None:
    spec = CircuitSpec(
        code_family="surface_code_rotated_memory",
        distance=3,
        rounds=3,
        logical_basis="z",
    )
    noisy = apply_noise(spec, NoiseSpec())
    dem = build_detector_error_model(noisy)

    assert dem.num_detectors > 0
    assert dem.num_errors > 0
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_noise_and_dem.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/qec_rd/specs.py src/qec_rd/circuit_generation.py src/qec_rd/noise.py src/qec_rd/dem.py tests/test_noise_and_dem.py
git commit -m "feat: add noise specs and dem extraction"
```

## Task 4: Add decoder abstraction and a PyMatching baseline

**Files:**
- Create: `src/qec_rd/decoders/__init__.py`
- Create: `src/qec_rd/decoders/base.py`
- Create: `src/qec_rd/decoders/pymatching_decoder.py`
- Test: `tests/test_pymatching_decoder.py`

- [ ] **Step 1: Write the failing decoder tests**

```python
# tests/test_pymatching_decoder.py
from qec_rd.decoders.pymatching_decoder import decode_logical_error_rate
from qec_rd.specs import CircuitSpec, NoiseSpec


def test_decode_logical_error_rate_returns_probability() -> None:
    rate = decode_logical_error_rate(
        circuit_spec=CircuitSpec(
            code_family="surface_code_rotated_memory",
            distance=3,
            rounds=3,
            logical_basis="z",
        ),
        noise_spec=NoiseSpec(after_clifford_depolarization=0.001),
        shots=100,
    )

    assert 0.0 <= rate <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pymatching_decoder.py -v`
Expected: FAIL with missing decoder module or symbol

- [ ] **Step 3: Implement the decoder abstraction and PyMatching path**

```python
# src/qec_rd/decoders/base.py
from dataclasses import dataclass


@dataclass(frozen=True)
class DecodeResult:
    logical_error_rate: float
    shots: int
    num_errors: int
```

```python
# src/qec_rd/decoders/pymatching_decoder.py
import numpy as np
import pymatching

from qec_rd.circuit_generation import build_circuit
from qec_rd.decoders.base import DecodeResult
from qec_rd.specs import CircuitSpec, NoiseSpec


def run_pymatching_decode(
    circuit_spec: CircuitSpec,
    noise_spec: NoiseSpec,
    shots: int,
) -> DecodeResult:
    circuit = build_circuit(circuit_spec, noise=noise_spec)
    dem = circuit.detector_error_model(decompose_errors=True)
    matching = pymatching.Matching.from_detector_error_model(dem)
    sampler = circuit.compile_detector_sampler()
    dets, obs = sampler.sample(shots=shots, separate_observables=True)
    predictions = matching.decode_batch(dets)
    num_errors = int(np.count_nonzero(predictions != obs[:, 0]))
    return DecodeResult(
        logical_error_rate=num_errors / shots,
        shots=shots,
        num_errors=num_errors,
    )


def decode_logical_error_rate(
    circuit_spec: CircuitSpec,
    noise_spec: NoiseSpec,
    shots: int,
) -> float:
    return run_pymatching_decode(circuit_spec, noise_spec, shots).logical_error_rate
```

```python
# src/qec_rd/decoders/__init__.py
from qec_rd.decoders.base import DecodeResult
from qec_rd.decoders.pymatching_decoder import (
    decode_logical_error_rate,
    run_pymatching_decode,
)

__all__ = ["DecodeResult", "decode_logical_error_rate", "run_pymatching_decode"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_pymatching_decoder.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/qec_rd/decoders/__init__.py src/qec_rd/decoders/base.py src/qec_rd/decoders/pymatching_decoder.py tests/test_pymatching_decoder.py
git commit -m "feat: add pymatching decoder baseline"
```

## Task 5: Add experiment orchestration, CSV/Markdown reports, and a usable CLI

**Files:**
- Create: `src/qec_rd/experiments.py`
- Create: `src/qec_rd/reporting.py`
- Modify: `src/qec_rd/cli.py`
- Test: `tests/test_cli_experiment.py`
- Create: `docs/architecture/foundation-mvp.md`

- [ ] **Step 1: Write the failing CLI experiment test**

```python
# tests/test_cli_experiment.py
from pathlib import Path

from typer.testing import CliRunner

from qec_rd.cli import app


def test_run_experiment_writes_csv(tmp_path: Path) -> None:
    runner = CliRunner()
    output_csv = tmp_path / "results.csv"

    result = runner.invoke(
        app,
        [
            "run-experiment",
            "--code-family", "surface_code_rotated_memory",
            "--distance", "3",
            "--rounds", "3",
            "--logical-basis", "z",
            "--after-clifford", "0.001",
            "--shots", "100",
            "--output-csv", str(output_csv),
        ],
    )

    assert result.exit_code == 0
    assert output_csv.exists()
    assert "logical_error_rate" in output_csv.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_experiment.py -v`
Expected: FAIL because `run-experiment` does not accept these options or does not write output

- [ ] **Step 3: Implement experiment and reporting modules**

```python
# src/qec_rd/experiments.py
from dataclasses import asdict, dataclass

from qec_rd.decoders.pymatching_decoder import run_pymatching_decode
from qec_rd.specs import CircuitSpec, NoiseSpec


@dataclass(frozen=True)
class ExperimentRecord:
    code_family: str
    distance: int
    rounds: int
    logical_basis: str
    shots: int
    after_clifford_depolarization: float
    before_round_data_depolarization: float
    before_measure_flip_probability: float
    after_reset_flip_probability: float
    logical_error_rate: float
    num_errors: int

    def to_dict(self) -> dict:
        return asdict(self)


def run_experiment(
    circuit_spec: CircuitSpec,
    noise_spec: NoiseSpec,
    shots: int,
) -> ExperimentRecord:
    result = run_pymatching_decode(circuit_spec, noise_spec, shots)
    return ExperimentRecord(
        code_family=circuit_spec.code_family,
        distance=circuit_spec.distance,
        rounds=circuit_spec.rounds,
        logical_basis=circuit_spec.logical_basis,
        shots=shots,
        after_clifford_depolarization=noise_spec.after_clifford_depolarization,
        before_round_data_depolarization=noise_spec.before_round_data_depolarization,
        before_measure_flip_probability=noise_spec.before_measure_flip_probability,
        after_reset_flip_probability=noise_spec.after_reset_flip_probability,
        logical_error_rate=result.logical_error_rate,
        num_errors=result.num_errors,
    )
```

```python
# src/qec_rd/reporting.py
from pathlib import Path

import pandas as pd

from qec_rd.experiments import ExperimentRecord


def write_csv(record: ExperimentRecord, output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([record.to_dict()]).to_csv(output_csv, index=False)


def write_markdown_summary(record: ExperimentRecord, output_md: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# QEC Experiment Summary",
        "",
        f"- code_family: `{record.code_family}`",
        f"- distance: `{record.distance}`",
        f"- rounds: `{record.rounds}`",
        f"- logical_basis: `{record.logical_basis}`",
        f"- shots: `{record.shots}`",
        f"- logical_error_rate: `{record.logical_error_rate:.6f}`",
        f"- num_errors: `{record.num_errors}`",
    ]
    output_md.write_text("\n".join(lines), encoding="utf-8")
```

- [ ] **Step 4: Replace the CLI placeholder with the actual command**

```python
# src/qec_rd/cli.py
from pathlib import Path

import typer

from qec_rd.experiments import run_experiment
from qec_rd.reporting import write_csv, write_markdown_summary
from qec_rd.specs import CircuitSpec, NoiseSpec

app = typer.Typer(
    help="QEC R&D foundation CLI for circuit generation, decoding, and analysis."
)


@app.command("run-experiment")
def run_experiment_command(
    code_family: str = typer.Option(...),
    distance: int = typer.Option(...),
    rounds: int = typer.Option(...),
    logical_basis: str = typer.Option(...),
    after_clifford: float = typer.Option(0.001),
    before_round_data: float = typer.Option(0.001),
    before_measure_flip: float = typer.Option(0.001),
    after_reset_flip: float = typer.Option(0.001),
    shots: int = typer.Option(1000),
    output_csv: Path = typer.Option(...),
    output_md: Path | None = typer.Option(None),
) -> None:
    circuit_spec = CircuitSpec(
        code_family=code_family,
        distance=distance,
        rounds=rounds,
        logical_basis=logical_basis,
    )
    noise_spec = NoiseSpec(
        after_clifford_depolarization=after_clifford,
        before_round_data_depolarization=before_round_data,
        before_measure_flip_probability=before_measure_flip,
        after_reset_flip_probability=after_reset_flip,
    )
    record = run_experiment(circuit_spec, noise_spec, shots)
    write_csv(record, output_csv)
    if output_md is not None:
        write_markdown_summary(record, output_md)
    typer.echo(f"logical_error_rate={record.logical_error_rate:.6f}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 5: Add architecture notes for future contributors**

```markdown
# docs/architecture/foundation-mvp.md
# Foundation MVP Architecture

The foundation MVP intentionally limits the platform to Stim-compatible stabilizer circuits and Pauli-style noise so the repository gains a reliable baseline before adding tensor-network simulation or hardware-calibrated models.

## Boundaries

- `specs.py` defines portable experiment inputs
- `circuit_generation.py` owns Stim-backed circuit construction
- `noise.py` owns noise application via generation-time parameters
- `dem.py` owns DEM extraction
- `decoders/` owns decoder implementations and decoder-facing result types
- `experiments.py` orchestrates one runnable experiment
- `reporting.py` owns persistence and human-readable summaries
- `cli.py` owns the external command-line surface

## Deliberate omissions

- No coherent-noise simulation
- No tensor-network backend
- No hardware calibration ingestion
- No FTQC resource estimator

These belong to follow-on plans after the baseline pipeline is stable.
```

- [ ] **Step 6: Run the focused tests**

Run: `python -m pytest tests/test_package_smoke.py tests/test_circuit_generation.py tests/test_noise_and_dem.py tests/test_pymatching_decoder.py tests/test_cli_experiment.py -v`
Expected: PASS

- [ ] **Step 7: Run the CLI manually**

Run:

```bash
python -m qec_rd.cli run-experiment --code-family surface_code_rotated_memory --distance 3 --rounds 3 --logical-basis z --after-clifford 0.001 --shots 100 --output-csv outputs/foundation_mvp.csv --output-md outputs/foundation_mvp.md
```

Expected:
- command exits with code 0
- `outputs/foundation_mvp.csv` exists
- `outputs/foundation_mvp.md` exists
- stdout contains `logical_error_rate=`

- [ ] **Step 8: Commit**

```bash
git add src/qec_rd/experiments.py src/qec_rd/reporting.py src/qec_rd/cli.py tests/test_cli_experiment.py docs/architecture/foundation-mvp.md
git commit -m "feat: add foundation experiment cli and reporting"
```

## Task 6: Add a thin repository README section for the MVP workflow

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add an MVP quickstart section**

```markdown
## Foundation MVP Quickstart

### Install

~~~bash
python -m pip install -e .[dev]
~~~

### Run tests

~~~bash
python -m pytest -v
~~~

### Run one experiment

~~~bash
python -m qec_rd.cli run-experiment --code-family surface_code_rotated_memory --distance 3 --rounds 3 --logical-basis z --after-clifford 0.001 --shots 1000 --output-csv outputs/example.csv --output-md outputs/example.md
~~~
```

- [ ] **Step 2: Run the full test suite**

Run: `python -m pytest -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add foundation mvp quickstart"
```

## Self-Review

### Spec coverage

- Circuit generation: covered by Task 2
- Realistic but bounded noise modeling: covered by Task 3 for Pauli-style baseline noise only
- DEM extraction: covered by Task 3
- Decoding analysis: covered by Task 4
- Experiment reporting / engineering workflow: covered by Task 5 and Task 6
- Coherent noise, tensor simulation, hardware integration, and FTQC estimation: intentionally deferred to separate plans

### Placeholder scan

- No `TODO`, `TBD`, or `"implement later"` markers remain in task steps
- Every test and code step includes concrete file paths, commands, and code blocks

### Type consistency

- `CircuitSpec` and `NoiseSpec` naming is consistent across tasks
- `run_experiment` and `run_experiment_command` names are consistent across modules
- `DecodeResult` field names match later reporting usage
