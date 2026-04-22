import numpy as np

from qec_rd.api import build_circuit, sample_syndromes
from qec_rd.core import CodeSpec, NoiseModel


def test_sample_syndromes_returns_standard_batch():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    batch = sample_syndromes(circuit, shots=8, seed=11)

    assert batch.shot_count == 8
    assert batch.detection_events.shape[0] == 8
    assert batch.observable_flips.shape[0] == 8
    assert batch.measurements is None
    assert batch.detection_events.dtype == np.bool_
    assert batch.source == "stim.detector_sampler"


def test_sample_syndromes_varies_with_seed():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=0.1),
    )
    batch_a = sample_syndromes(circuit, shots=100, seed=1)
    batch_b = sample_syndromes(circuit, shots=100, seed=2)
    # With high noise and many shots, different seeds should almost certainly differ.
    assert not np.array_equal(batch_a.detection_events, batch_b.detection_events)
