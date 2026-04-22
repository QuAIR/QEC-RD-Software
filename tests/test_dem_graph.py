import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.api import build_circuit, build_decoding_graph, extract_dem
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
