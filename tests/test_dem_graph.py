import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.api import (
    build_circuit,
    build_decoding_graph,
    extract_dem,
    run_decoder,
    sample_syndromes,
)
from qec_rd.core import CodeSpec, NoiseModel


def test_extract_dem_and_build_graph_for_generated_repetition_memory():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)

    assert dem.num_detectors > 0
    assert dem.num_observables >= 1
    assert graph.num_detectors == dem.num_detectors
    assert graph.check_matrix.shape[0] == dem.num_detectors
    assert graph.observable_matrix.shape[0] == dem.num_observables
    assert np.all(graph.error_probabilities > 0.0)


def test_extract_dem_returns_dem_artifact():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)

    assert dem.num_detectors > 0
    assert dem.num_observables >= 1
    assert dem.dem_text
    assert dem.raw_handle is not None


def test_build_decoding_graph_from_dem_artifact():
    circuit = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)
    graph = build_decoding_graph(dem)

    assert graph.num_detectors == dem.num_detectors
    assert graph.num_observables == dem.num_observables
    assert graph.check_matrix.shape[0] == dem.num_detectors
    assert isinstance(graph.check_matrix, csc_matrix)
    assert isinstance(graph.observable_matrix, np.ndarray)
    assert np.all(graph.error_probabilities > 0.0)
    assert len(graph.edge_fault_ids) == graph.check_matrix.shape[1]


def test_build_decoding_graph_handles_stim_separator_decomposed_errors():
    circuit = build_circuit(
        CodeSpec(family="rotated_surface_code", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    dem = extract_dem(circuit)

    graph = build_decoding_graph(dem)
    batch = sample_syndromes(circuit, shots=8, seed=13)
    result = run_decoder(graph, batch, decoder_name="pymatching")

    assert graph.num_detectors == dem.num_detectors
    assert graph.check_matrix.shape[1] > 0
    assert result.predicted_observables.shape == batch.observable_flips.shape


def test_build_decoding_graph_supports_noisy_surface_and_toric_graphlike_dems():
    for family in (
        "rotated_surface_code",
        "unrotated_surface_code",
        "toric_code",
    ):
        circuit = build_circuit(
            CodeSpec(family=family, distance=3, rounds=3),
            NoiseModel(after_clifford_depolarization=1e-3),
        )
        dem = extract_dem(circuit)

        graph = build_decoding_graph(dem)
        batch = sample_syndromes(circuit, shots=8, seed=17)
        result = run_decoder(graph, batch, decoder_name="pymatching")

        assert graph.check_matrix.shape[0] == dem.num_detectors
        assert graph.observable_matrix.shape[0] == dem.num_observables
        assert np.max(graph.check_matrix.getnnz(axis=0)) <= 2
        assert result.predicted_observables.shape == batch.observable_flips.shape
