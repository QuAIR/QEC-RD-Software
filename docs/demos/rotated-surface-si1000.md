# Demo 2: What Counts as a Noise Model Here?

This second demo introduces the next keyword category: `noise`.
The user still does not need to make open-ended choices. The goal is just to
understand what a phrase like

```text
si1000 noise
```

means inside this repository.

Stage 1 keeps noise limited to Stim-executable Pauli-style presets:

- `toy`
- `toy_phenomenological`
- `sd6`
- `si1000`
- `stim_circuit_level_si1000`

## What This Demo Should Teach

- Noise models in Stage 1 are platform-defined presets, not arbitrary channels.
- `si1000` is the main scheduled superconducting-style preset used by the final acceptance demo.
- Different presets fill different fields of `NoiseModel`.
- Non-Pauli behavior and leakage are intentionally out of scope.

## Run

```python
from qec_rd.api import NoiseModel

presets = {
    "toy": NoiseModel.toy(p=0.001),
    "toy_phenomenological": NoiseModel.toy_phenomenological(p=0.001),
    "sd6": NoiseModel.sd6(p=0.001),
    "si1000": NoiseModel.si1000(p=0.001),
    "stim_circuit_level_si1000": NoiseModel.stim_circuit_level_si1000(p=0.001),
}

for name, noise in presets.items():
    print(name, noise)
```

## Expected Shape

You should see the same data class shape for every preset, but with different
fields populated. In particular, scheduled `si1000` should include idle-related
fields that the coarse circuit-level preset does not.

## Why This Matters for the Later Demos

Once the reader understands `code` and `noise`, the next question becomes:
"What decoder am I using, and am I asking for a single logical error rate or a
distance sweep toward threshold?"
