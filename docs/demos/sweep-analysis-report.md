# Demo 4: How a Full Experiment Description Is Assembled

This fourth demo is the bridge from concepts to execution.
It does not ask the user to make free choices. Instead, it shows how a simple
natural-language-style description can be understood as four keyword slots:

- `code`
- `noise`
- `decoder`
- `target`

For example, the phrase

```text
rotated surface code, si1000 noise, mwpm, ler
```

can be read as:

- `code = rotated_surface_code`
- `noise = si1000`
- `decoder = pymatching`
- `target = ler`

## What This Demo Should Teach

- The later acceptance demo is not magic; it is just a fixed experiment recipe.
- A natural-language description can be normalized into `ExperimentConfig`.
- `LER` maps to one experiment run.
- `threshold` would map to a distance sweep instead of a single run.

## Run

```python
from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, run_experiment

keywords = {
    "code": "rotated_surface_code",
    "noise": "si1000",
    "decoder": "pymatching",
    "target": "ler",
}

config = ExperimentConfig(
    code_spec=CodeSpec(
        family=keywords["code"],
        distance=3,
        rounds=3,
        logical_basis="Z",
    ),
    noise_spec=NoiseModel.si1000(p=0.001),
    decoder_spec={"name": keywords["decoder"]},
    sim_spec={"shots": 100, "seed": 11},
)

result = run_experiment(config)

print("keywords:", keywords)
print("shots:", result.analysis_report.shot_count)
print("logical_error_rate:", result.analysis_report.logical_error_rate)
```

## Expected Shape

The printed keyword dictionary should match the experiment configuration, and
the run should return a valid `logical_error_rate`.

## What Comes Next

The fifth and final demo stops being conceptual.
It fixes the experiment recipe to the acceptance path and produces the actual
review result.
