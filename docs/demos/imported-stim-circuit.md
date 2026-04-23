# Demo 3: Imported Stim Circuit Pipeline

Circuit import is the main Stage 1 customization path. This demo writes a generated circuit to a `.stim` file, reloads it through the public API, and runs the same DEM, sampling, decoding, and analysis flow on the imported artifact.

## What This Verifies

- Circuit customization through import
- `CircuitArtifact` source tracking for imported Stim files
- DEM extraction from imported circuits
- Decoder and analysis compatibility with imported artifacts

## Run

```python
from pathlib import Path

from qec_rd.api import (
    CodeSpec,
    NoiseModel,
    analyze_results,
    build_circuit,
    build_decoding_graph,
    extract_dem,
    load_circuit,
    run_decoder,
    sample_syndromes,
)

source = build_circuit(
    CodeSpec("repetition_code:memory", distance=3, rounds=3),
    NoiseModel(after_clifford_depolarization=0.001),
)

path = Path("imported_memory_demo.stim")
path.write_text(str(source.raw_handle), encoding="utf-8")

imported = load_circuit(path)
dem = extract_dem(imported)
graph = build_decoding_graph(dem)
batch = sample_syndromes(imported, shots=64, seed=23)
decoded = run_decoder(graph, batch, decoder_name="pymatching")
report = analyze_results(decoded)

print("source_kind:", imported.source_kind.value)
print("source_path:", imported.origin_metadata["source_path"])
print("shots:", report.shot_count)
print("logical_error_rate:", report.logical_error_rate)
```

## Expected Shape

The imported artifact should report `source_kind` as an imported Stim file and should run through the same decoding path as a generated circuit.
