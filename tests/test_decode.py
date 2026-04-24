import numpy as np

from qec_rd.core import CodeSpec, ExperimentConfig, NoiseModel
from qec_rd.kernel.circuit import build_circuit
from qec_rd.kernel.decode import run_decoder
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes
from qec_rd.kernel.runner import run_experiment


def test_run_decoder_supports_bposd_for_graphlike_dem() -> None:
    circuit = build_circuit(
        CodeSpec("rotated_surface_code", distance=3, rounds=3),
        NoiseModel.si1000(p=0.01),
    )
    graph = build_decoding_graph(extract_dem(circuit))
    batch = sample_syndromes(circuit, shots=8, seed=5)

    result = run_decoder(graph, batch, decoder_name="bposd")

    assert result.decoder_name == "bposd"
    assert result.predicted_observables.shape == batch.observable_flips.shape
    assert result.failure_mask.shape == (batch.shot_count,)
    assert result.metadata["backend"] == "ldpc"
    assert result.metadata["osd_method"] == "osd_0"


def test_bposd_matches_pymatching_on_zero_noise_rotated_surface() -> None:
    circuit = build_circuit(
        CodeSpec("rotated_surface_code", distance=3, rounds=3),
        NoiseModel(),
    )
    graph = build_decoding_graph(extract_dem(circuit))
    batch = sample_syndromes(circuit, shots=6, seed=13)

    mwpm = run_decoder(graph, batch, decoder_name="pymatching")
    bposd = run_decoder(graph, batch, decoder_name="bposd")

    np.testing.assert_array_equal(
        bposd.predicted_observables,
        mwpm.predicted_observables,
    )
    np.testing.assert_array_equal(bposd.failure_mask, mwpm.failure_mask)


def test_run_experiment_accepts_bposd_decoder_spec() -> None:
    result = run_experiment(
        ExperimentConfig(
            code_spec=CodeSpec("rotated_surface_code", distance=3, rounds=3),
            noise_spec=NoiseModel.si1000(p=0.01),
            decoder_spec={"name": "bposd", "osd_order": 0},
            sim_spec={"shots": 10, "seed": 17},
        )
    )

    assert result.decode_result.decoder_name == "bposd"
    assert result.analysis_report.shot_count == 10
