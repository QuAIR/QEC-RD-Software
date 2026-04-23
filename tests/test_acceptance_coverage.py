from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import stim
from scipy.sparse import csc_matrix

from qec_rd.core import (
    CodeSpec,
    DecodeResult,
    DecoderConfigurationError,
    DecodingGraph,
    DemArtifact,
    ExperimentConfig,
    NoiseModel,
    QecRdError,
    RepetitionCode,
    StabilizerSpec,
    SyndromeBatch,
    noise_model_from_spec,
)
from qec_rd.core.builtin_codes import BuiltinCode, builtin_code_from_spec
from qec_rd.kernel.analysis import analyze_results
from qec_rd.kernel.circuit import build_circuit
from qec_rd.kernel.decode import normalize_custom_decode_result, run_decoder
from qec_rd.kernel.graph import build_decoding_graph
from qec_rd.kernel.memory import _record_stabilizer_measurements, build_memory_circuit
from qec_rd.kernel.runner import (
    ExperimentRunner,
    _combine_decode_results,
    _combine_syndrome_batches,
    benchmark,
    run_experiment,
    sweep,
)


def _minimal_graph(raw_dem_handle=None) -> DecodingGraph:
    return DecodingGraph(
        num_detectors=1,
        num_observables=1,
        check_matrix=csc_matrix([[1]], dtype=np.uint8),
        observable_matrix=np.array([[1]], dtype=np.uint8),
        error_probabilities=np.array([0.1]),
        edge_fault_ids=[0],
        raw_dem_handle=raw_dem_handle,
    )


def _minimal_batch() -> SyndromeBatch:
    return SyndromeBatch(
        detection_events=np.zeros((2, 1), dtype=np.bool_),
        observable_flips=np.zeros((2, 1), dtype=np.bool_),
        measurements=None,
        shot_count=2,
        seed=3,
        source="unit",
    )


def test_decoder_error_paths_and_custom_decoder_hook() -> None:
    graph = _minimal_graph()
    batch = _minimal_batch()

    with pytest.raises(DecoderConfigurationError, match="raw DEM"):
        run_decoder(graph, batch, decoder_name="pymatching")
    with pytest.raises(DecoderConfigurationError, match="decoder_fn"):
        run_decoder(graph, batch, decoder_name="custom")
    with pytest.raises(DecoderConfigurationError, match="Unsupported"):
        run_decoder(graph, batch, decoder_name="unknown")

    def wrong_decoder(_graph, _batch):
        return {"not": "a DecodeResult"}

    with pytest.raises(DecoderConfigurationError, match="DecodeResult"):
        run_decoder(graph, batch, decoder_name="custom", decoder_fn=wrong_decoder)

    def custom_decoder(_graph, incoming_batch, tag: str) -> DecodeResult:
        return normalize_custom_decode_result(
            decoder_name="custom-demo",
            predicted_observables=np.zeros((incoming_batch.shot_count, 1), dtype=np.bool_),
            actual_observables=None,
            metadata={"tag": tag},
        )

    result = run_decoder(
        graph,
        batch,
        decoder_name="custom",
        decoder_fn=custom_decoder,
        tag="acceptance",
    )

    assert result.decoder_name == "custom-demo"
    assert result.metadata == {"tag": "acceptance"}
    assert result.failure_count == 0


def test_noise_model_rejects_non_pauli_leakage_and_unknown_presets() -> None:
    with pytest.raises(ValueError, match="non-Pauli"):
        NoiseModel.si1000(p=0.001, pL=0.1)
    with pytest.raises(ValueError, match="non-Pauli"):
        NoiseModel.stim_circuit_level_si1000(p=0.001, pL=0.1)
    with pytest.raises(ValueError, match="Unsupported noise model preset"):
        noise_model_from_spec({"name": "not-a-real-noise-model"})


def test_code_and_builtin_validation_error_paths() -> None:
    with pytest.raises(ValueError, match="distance"):
        CodeSpec("repetition_code:memory", distance=0, rounds=1)
    with pytest.raises(ValueError, match="rounds"):
        CodeSpec("repetition_code:memory", distance=1, rounds=0)
    with pytest.raises(ValueError, match="stabilizer basis"):
        StabilizerSpec("Y", (0, 0), ((0, 1),))
    with pytest.raises(ValueError, match="distance"):
        BuiltinCode(
            family="bad",
            distance=0,
            data_coords=(),
            x_ancilla_coords=(),
            z_ancilla_coords=(),
            x_stabilizers=(),
            z_stabilizers=(),
            x_logical=(),
            z_logical=(),
        )
    with pytest.raises(ValueError, match="stabilizer_basis"):
        RepetitionCode(distance=3, stabilizer_basis="Y")

    class UnknownSpec:
        family = "unknown"
        distance = 3
        rounds = 3
        logical_basis = "Z"

    with pytest.raises(ValueError, match="unsupported"):
        builtin_code_from_spec(UnknownSpec())  # type: ignore[arg-type]


def test_memory_circuit_validation_and_measurement_recording_paths() -> None:
    code = RepetitionCode(distance=3, stabilizer_basis="Z")

    with pytest.raises(ValueError, match="logical_basis"):
        build_memory_circuit(code, logical_basis="Y", rounds=1)
    with pytest.raises(ValueError, match="rounds"):
        build_memory_circuit(code, logical_basis="Z", rounds=0)
    with pytest.raises(QecRdError, match="same stabilizer basis"):
        build_memory_circuit(code, logical_basis="X", rounds=1)

    lines: list[str] = []
    previous = {("Z", code.z_stabilizers[0].ancilla): 0}
    measurement_count = _record_stabilizer_measurements(
        lines=lines,
        stabilizers=code.z_stabilizers,
        measure_basis="Z",
        logical_basis="Z",
        measurement_count=1,
        previous_measurements=previous,
    )

    assert measurement_count == 3
    assert any(line.startswith("DETECTOR") for line in lines)


def test_runner_entry_points_and_circuit_import_path(tmp_path: Path) -> None:
    config = ExperimentConfig(
        code_spec=CodeSpec("repetition_code:memory", distance=3, rounds=3),
        noise_spec=NoiseModel(after_clifford_depolarization=0.001),
        decoder_spec={"name": "pymatching"},
        sim_spec={"shots": 3, "seed": 5},
    )

    single = run_experiment(config)
    assert single.syndrome_batch.shot_count == 3

    repeated = benchmark(config, repeats=2)
    assert [item.syndrome_batch.shot_count for item in repeated] == [3, 3]

    swept = sweep(config, "sim_spec.shots", [1, 2])
    assert [item.syndrome_batch.shot_count for item in swept] == [1, 2]

    path = tmp_path / "imported.stim"
    path.write_text(str(build_circuit(config.code_spec, config.noise_spec).raw_handle), encoding="utf-8")
    imported_config = ExperimentConfig(
        circuit_spec={"source": path, "format": "stim"},
        decoder_spec={"name": "pymatching"},
        sim_spec={"shots": 2, "seed": 9},
    )

    circuit, graph = ExperimentRunner().prepare(imported_config)

    assert circuit.source_format == "stim"
    assert graph.num_detectors > 0


def test_runner_batch_combining_edge_paths() -> None:
    with pytest.raises(ValueError, match="empty"):
        _combine_syndrome_batches([])
    with pytest.raises(ValueError, match="empty"):
        _combine_decode_results("custom", [])

    first_batch = SyndromeBatch(
        detection_events=np.zeros((1, 1), dtype=np.bool_),
        observable_flips=np.zeros((1, 1), dtype=np.bool_),
        measurements=np.zeros((1, 2), dtype=np.bool_),
        shot_count=1,
        seed=1,
        source="unit",
    )
    second_batch = SyndromeBatch(
        detection_events=np.ones((1, 1), dtype=np.bool_),
        observable_flips=None,
        measurements=None,
        shot_count=1,
        seed=2,
        source="unit",
    )

    combined_batch = _combine_syndrome_batches([first_batch, second_batch])

    assert combined_batch.shot_count == 2
    assert combined_batch.observable_flips is None
    assert combined_batch.measurements is None

    first_result = DecodeResult(
        decoder_name="custom",
        predicted_observables=np.zeros((1, 1), dtype=np.bool_),
        actual_observables=np.zeros((1, 1), dtype=np.bool_),
        corrections=np.zeros((1, 1), dtype=np.bool_),
        failure_mask=np.zeros(1, dtype=np.bool_),
        metadata={"batch": 1},
    )
    second_result = DecodeResult(
        decoder_name="custom",
        predicted_observables=np.ones((1, 1), dtype=np.bool_),
        actual_observables=None,
        corrections=None,
        failure_mask=np.ones(1, dtype=np.bool_),
        metadata={"batch": 2},
    )

    combined_result = _combine_decode_results("custom", [first_result, second_result])

    assert combined_result.actual_observables is None
    assert combined_result.corrections is None
    assert combined_result.failure_count == 1
    assert combined_result.metadata["num_batches"] == 2


def test_run_until_failures_rejects_invalid_stop_parameters() -> None:
    config = ExperimentConfig(
        code_spec=CodeSpec("repetition_code:memory", distance=3, rounds=3),
        decoder_spec={"name": "pymatching"},
        sim_spec={"shots": 1, "seed": 1},
    )
    runner = ExperimentRunner()

    with pytest.raises(ValueError, match="min_failures"):
        runner.run_until_failures(config, min_failures=0, max_shots=1, batch_size=1)
    with pytest.raises(ValueError, match="max_shots"):
        runner.run_until_failures(config, min_failures=1, max_shots=0, batch_size=1)
    with pytest.raises(ValueError, match="batch_size"):
        runner.run_until_failures(config, min_failures=1, max_shots=1, batch_size=0)


def test_analysis_handles_empty_and_unverified_custom_results() -> None:
    unverified = normalize_custom_decode_result(
        decoder_name="custom",
        predicted_observables=np.zeros((2, 1), dtype=np.bool_),
        actual_observables=None,
    )

    unverified_report = analyze_results(unverified)
    empty_report = analyze_results([])

    assert unverified_report.logical_error_distribution == {}
    assert unverified_report.metadata["logical_event_count"] == 0
    assert empty_report.decoder_name == "unknown"
    assert empty_report.shot_count == 0


def test_load_circuit_rejects_non_stim_file_suffix(tmp_path: Path) -> None:
    path = tmp_path / "bad.qasm"
    path.write_text("OPENQASM 2.0;", encoding="utf-8")

    with pytest.raises(Exception, match="Unsupported circuit format"):
        ExperimentRunner().prepare(
            ExperimentConfig(
                circuit_spec={"source": path, "format": "stim"},
                decoder_spec={"name": "pymatching"},
            )
        )


def test_graph_skips_empty_dem_error_terms() -> None:
    dem = stim.DetectorErrorModel("error(0.125)\n")
    graph = build_decoding_graph(
        DemArtifact(
            num_detectors=0,
            num_observables=0,
            dem_text=str(dem),
            raw_handle=dem,
        )
    )

    assert graph.check_matrix.shape == (0, 0)
    assert graph.error_probabilities.size == 0
