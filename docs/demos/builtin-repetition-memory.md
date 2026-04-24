# Demo 1: What Counts as a Code Here?

This first demo is for a reader who does not yet know QEC terminology.
Its job is not to let the user choose arbitrarily. Its job is to teach the
first keyword category: `code`.

In Stage 1, the platform owns a small built-in code catalog:

- `repetition_code:memory`
- `rotated_surface_code`
- `unrotated_surface_code`
- `toric_code`

When a later demo says something like:

```text
rotated surface code
```

it really means: "use the built-in circuit generator for the
`rotated_surface_code` family".

## What This Demo Should Teach

- A "code" in this repo means a built-in circuit family or an imported circuit.
- The public interface still starts from `CodeSpec`.
- Different code families lead to different detector counts and circuit sizes.
- The user does not need to understand stabilizer internals before running the later demos.

## Run

```python
from qec_rd.api import CodeSpec, NoiseModel, build_circuit, extract_dem

families = [
    "repetition_code:memory",
    "rotated_surface_code",
    "unrotated_surface_code",
    "toric_code",
]

for family in families:
    circuit = build_circuit(
        CodeSpec(family=family, distance=3, rounds=3, logical_basis="Z"),
        NoiseModel(),
    )
    dem = extract_dem(circuit)
    print(
        family,
        "detectors=",
        dem.num_detectors,
        "observables=",
        dem.num_observables,
    )
```

## Expected Shape

The exact detector counts differ by code family, but every built-in family above
should produce a valid circuit and DEM.

## Why This Matters for the Later Demos

The next demos will introduce `noise`, `decoder`, and `target`.
For the final acceptance path, we will eventually fix the code keyword to
`rotated surface code`.
