# Demo 2: Rotated Surface Memory With Scheduled SI1000-Style Noise

This demo exercises the Stage 1 surface-code path with the platform-owned scheduled SI1000-style noise model. The model is Stim-executable and does not include leakage.

## What This Verifies

- Built-in `rotated_surface_code`
- Platform-owned surface-code circuit construction
- Scheduled SI1000-style Stim-executable noise
- MWPM decoding through `pymatching`
- Logical-error-rate analysis

## Run

```python
from qec_rd.api import ExperimentConfig, CodeSpec, NoiseModel, run_experiment

config = ExperimentConfig(
    code_spec=CodeSpec(
        family="rotated_surface_code",
        distance=3,
        rounds=3,
        logical_basis="Z",
    ),
    noise_spec=NoiseModel.si1000(p=0.001),
    decoder_spec={"name": "pymatching"},
    sim_spec={"shots": 100, "seed": 11},
)

result = run_experiment(config)

print("circuit_source:", result.circuit.source_kind.value)
print("shots:", result.analysis_report.shot_count)
print("failures:", result.analysis_report.failure_count)
print("logical_error_rate:", result.analysis_report.logical_error_rate)
```

## Expected Shape

The demo should complete without relying on `stim.Circuit.generated` for the surface-code circuit. The report should contain 100 shots and a valid logical error rate.
