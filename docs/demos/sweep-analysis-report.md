# Demo 5: Parameter Sweep and Analysis Report

This demo validates the experiment-runner layer by sweeping over simulation shot counts and collecting analysis reports from each run.

## What This Verifies

- DeltaKit-style runner orchestration through `ExperimentConfig`
- Parameter sweep support
- Repeated end-to-end execution
- Analysis reports as the final user-facing research output

## Run

```python
from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, sweep

config = ExperimentConfig(
    code_spec=CodeSpec(
        family="repetition_code:memory",
        distance=3,
        rounds=3,
        logical_basis="Z",
    ),
    noise_spec=NoiseModel(after_clifford_depolarization=0.001),
    decoder_spec={"name": "pymatching"},
    sim_spec={"shots": 16, "seed": 41},
)

results = sweep(config, "sim_spec.shots", [16, 32, 64])

for result in results:
    report = result.analysis_report
    print(
        "shots=",
        report.shot_count,
        "failures=",
        report.failure_count,
        "ler=",
        report.logical_error_rate,
    )
```

## Expected Shape

The printed shot counts should be `16`, `32`, and `64`. Each result should contain a circuit artifact, sampled syndrome batch, decode result, and analysis report.
