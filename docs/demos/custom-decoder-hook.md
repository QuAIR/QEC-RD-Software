# Demo 4: Custom Decoder Hook

Stage 1 uses external decoder packages for built-in adapters, but it also allows custom decoder hooks. This demo plugs a simple decoder into the pipeline without changing DEM or graph construction.

## What This Verifies

- Custom decoder entry through the public `run_decoder` API
- Stable `DecodingGraph` and `SyndromeBatch` inputs
- Standard `DecodeResult` normalization
- Analysis compatibility with user-provided decoder logic

## Run

```python
import numpy as np

from qec_rd.api import (
    CodeSpec,
    NoiseModel,
    analyze_results,
    build_circuit,
    build_decoding_graph,
    extract_dem,
    normalize_custom_decode_result,
    run_decoder,
    sample_syndromes,
)


def zero_decoder(graph, batch):
    predicted = np.zeros_like(batch.observable_flips, dtype=np.bool_)
    return normalize_custom_decode_result(
        decoder_name="zero-decoder-demo",
        predicted_observables=predicted,
        actual_observables=batch.observable_flips,
        metadata={"graph_detectors": graph.num_detectors},
    )


circuit = build_circuit(
    CodeSpec("repetition_code:memory", distance=3, rounds=3),
    NoiseModel(after_clifford_depolarization=0.001),
)
graph = build_decoding_graph(extract_dem(circuit))
batch = sample_syndromes(circuit, shots=32, seed=31)
decoded = run_decoder(graph, batch, decoder_name="custom", decoder_fn=zero_decoder)
report = analyze_results(decoded)

print("decoder:", decoded.decoder_name)
print("graph_detectors:", decoded.metadata["graph_detectors"])
print("logical_error_rate:", report.logical_error_rate)
```

## Expected Shape

The demo should return a normal `DecodeResult` and `AnalysisReport`. The decoder is intentionally simple; the purpose is to verify hook integration, not decoder quality.
