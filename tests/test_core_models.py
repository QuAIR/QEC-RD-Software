import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.core import (
    AnalysisReport,
    CircuitArtifact,
    CircuitSourceKind,
    CodeSpec,
    DecodeResult,
    DecodingGraph,
    ExperimentConfig,
    ExperimentResult,
    NoiseModel,
    SyndromeBatch,
    noise_model_from_spec,
)


def test_core_objects_capture_stage1_metadata():
    code = CodeSpec(family="repetition_code:memory", distance=3, rounds=3)
    noise = NoiseModel(after_clifford_depolarization=1e-3)
    config = ExperimentConfig(code_spec=code, noise_spec=noise, decoder_spec={"name": "pymatching"})
    circuit = CircuitArtifact(
        source_kind=CircuitSourceKind.GENERATED,
        source_format="stim",
        code_spec=code,
        origin_metadata={"generator": "stim.generated"},
    )

    graph = DecodingGraph(
        num_detectors=3,
        num_observables=1,
        check_matrix=csc_matrix([[1, 0], [0, 1], [1, 1]], dtype=np.uint8),
        observable_matrix=np.array([[1, 0]], dtype=np.uint8),
        error_probabilities=np.array([0.1, 0.2]),
        edge_fault_ids=[0, 1],
        raw_dem_handle=None,
    )

    batch = SyndromeBatch(
        detection_events=np.zeros((4, 3), dtype=np.bool_),
        observable_flips=np.zeros((4, 1), dtype=np.bool_),
        measurements=None,
        shot_count=4,
        seed=5,
        source="stim.detector_sampler",
    )

    result = DecodeResult(
        decoder_name="pymatching",
        predicted_observables=np.zeros((4, 1), dtype=np.bool_),
        actual_observables=np.zeros((4, 1), dtype=np.bool_),
        corrections=np.zeros((4, 2), dtype=np.uint8),
        failure_mask=np.zeros(4, dtype=np.bool_),
        metadata={"distance": 3},
    )

    report = AnalysisReport(
        decoder_name="pymatching",
        shot_count=4,
        failure_count=0,
        logical_error_rate=0.0,
        logical_error_rate_stderr=0.0,
        metadata={"kind": "unit"},
    )
    experiment = ExperimentResult(
        config=config,
        circuit=circuit,
        syndrome_batch=batch,
        decode_result=result,
        analysis_report=report,
    )

    assert circuit.code_spec == code
    assert experiment.config == config
    assert noise.after_clifford_depolarization == 1e-3
    assert graph.check_matrix.shape == (3, 2)
    assert batch.shot_count == 4
    assert result.failure_count == 0
    assert report.logical_error_rate == 0.0


def test_noise_model_named_presets_map_to_stage1_stim_channels():
    assert NoiseModel.toy(p=0.01) == NoiseModel(
        after_clifford_depolarization=0.01,
        before_round_data_depolarization=0.001,
        before_measure_flip_probability=0.01,
        after_reset_flip_probability=0.001,
    )
    assert NoiseModel.toy(p=0.01, p_measurement_flip=0.02).before_measure_flip_probability == 0.02

    assert NoiseModel.toy_phenomenological(p=0.01) == NoiseModel(
        before_round_data_depolarization=0.01,
        before_measure_flip_probability=0.01,
    )
    assert NoiseModel.sd6(p=0.01) == NoiseModel(
        after_clifford_depolarization=0.01,
        before_round_data_depolarization=0.01,
        before_measure_flip_probability=0.01,
        after_reset_flip_probability=0.01,
    )
    assert NoiseModel.stim_circuit_level_si1000(p=0.01) == NoiseModel(
        after_clifford_depolarization=0.01,
        before_round_data_depolarization=0.001,
        before_measure_flip_probability=0.05,
        after_reset_flip_probability=0.02,
    )
    assert NoiseModel.si1000(p=0.01) == NoiseModel(
        after_clifford_depolarization=0.01,
        before_measure_flip_probability=0.05,
        after_reset_flip_probability=0.02,
        idle_depolarization=0.001,
        resonator_idle_depolarization=0.02,
    )


def test_noise_model_from_spec_accepts_named_and_raw_specs():
    assert noise_model_from_spec({"name": "sd6", "p": 0.01}) == NoiseModel.sd6(0.01)
    assert noise_model_from_spec({"model": "toy_phenomenological", "p": 0.02}) == (
        NoiseModel.toy_phenomenological(0.02)
    )
    assert noise_model_from_spec({"name": "ToyPhenomenologicalNoise", "p": 0.02}) == (
        NoiseModel.toy_phenomenological(0.02)
    )
    assert noise_model_from_spec({"name": "SI1000Noise", "p": 0.001}) == NoiseModel.si1000(
        0.001
    )
    assert noise_model_from_spec({"after_clifford_depolarization": 0.03}) == NoiseModel(
        after_clifford_depolarization=0.03
    )
    assert noise_model_from_spec(NoiseModel.si1000(0.001)) == NoiseModel.si1000(0.001)
    assert noise_model_from_spec(None) is None
