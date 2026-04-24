# Demo 3: What Counts as a Decoder and a Target?

This third demo introduces the final two keyword categories:

- `decoder`
- `target`

Examples of the phrases we want a beginner to recognize are:

```text
mwpm, ler
bposd, ler
mwpm, threshold
```

In Stage 1:

- built-in decoder adapters come from external packages
- `mwpm` means `pymatching`
- `bposd` means BP+OSD-0 through `ldpc`
- `ler` means one configured experiment
- `threshold` means a multi-distance sweep, not a single run

## What This Demo Should Teach

- Decoder choice and analysis target are different concepts.
- `LER` is a single-run output.
- `threshold` needs multiple distances and repeated end-to-end runs.
- The final acceptance demo fixes the decoder to `MWPM`.

## Run

```python
from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, run_experiment

base = dict(
    code_spec=CodeSpec(
        family="rotated_surface_code",
        distance=3,
        rounds=3,
        logical_basis="Z",
    ),
    noise_spec=NoiseModel.si1000(p=0.001),
    sim_spec={"shots": 100, "seed": 11},
)

for decoder_name in ["pymatching", "bposd"]:
    result = run_experiment(
        ExperimentConfig(
            **base,
            decoder_spec={"name": decoder_name, "osd_order": 0},
        )
    )
    print(
        decoder_name,
        "failures=",
        result.analysis_report.failure_count,
        "ler=",
        result.analysis_report.logical_error_rate,
    )
```

## Expected Shape

Both decoders should run through the same Stage 1 artifact chain and produce a
valid `logical_error_rate`.

## Why This Matters for the Later Demos

By this point the reader has seen the four core keywords:

- `code`
- `noise`
- `decoder`
- `target`

The next demo shows how those keywords are assembled into one complete
experiment description.
