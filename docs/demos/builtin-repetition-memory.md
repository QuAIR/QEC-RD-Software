# Demo 1: Built-in Repetition Memory Experiment

This demo validates the simplest built-in catalog path. It generates a repetition memory circuit, extracts a DEM, builds the decoding graph, samples syndromes, decodes with MWPM through `pymatching`, and reports the logical error rate.

## What This Verifies

- Built-in circuit catalog entry: `repetition_code:memory`
- Stim-backed memory circuit generation
- DEM extraction and platform-owned decoding graph construction
- Syndrome sampling
- MWPM decoding through an external package
- Analysis report generation

## Run

```python
from qec_rd.api import (
    CodeSpec,
    NoiseModel,
    analyze_results,
    build_circuit,
    build_decoding_graph,
    extract_dem,
    run_decoder,
    sample_syndromes,
)

code = CodeSpec(
    family="repetition_code:memory",
    distance=3,
    rounds=3,
    logical_basis="Z",
)
noise = NoiseModel(after_clifford_depolarization=0.001)

circuit = build_circuit(code, noise)
dem = extract_dem(circuit)
graph = build_decoding_graph(dem)
batch = sample_syndromes(circuit, shots=100, seed=7)
decoded = run_decoder(graph, batch, decoder_name="pymatching")
report = analyze_results(decoded)

print("detectors:", graph.num_detectors)
print("shots:", report.shot_count)
print("logical_error_rate:", report.logical_error_rate)
```

## Expected Shape

The exact logical error rate depends on stochastic sampling, but the result should have:

- `graph.num_detectors > 0`
- `report.shot_count == 100`
- `0.0 <= report.logical_error_rate <= 1.0`
