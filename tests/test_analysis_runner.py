import numpy as np

from qec_rd.core import CodeSpec, ExperimentConfig, NoiseModel
from qec_rd.kernel.runner import run_until_failures


def test_run_until_failures_stops_at_max_shots_when_failures_not_reached():
    result = run_until_failures(
        ExperimentConfig(
            code_spec=CodeSpec("repetition_code:memory", distance=3, rounds=3),
            noise_spec=NoiseModel(),
            decoder_spec={"name": "pymatching"},
            sim_spec={"seed": 7},
        ),
        min_failures=1,
        max_shots=6,
        batch_size=2,
    )

    assert result.syndrome_batch.shot_count == 6
    assert result.decode_result.failure_count == 0
    assert result.analysis_report.metadata["stop_reason"] == "max_shots"
    assert result.analysis_report.metadata["batches"] == 3


def test_run_until_failures_accumulates_batches_and_reports_logicals():
    result = run_until_failures(
        ExperimentConfig(
            code_spec=CodeSpec("rotated_surface_code", distance=3, rounds=3),
            noise_spec=NoiseModel.si1000(p=0.1),
            decoder_spec={"name": "pymatching"},
            sim_spec={"seed": 11},
        ),
        min_failures=1,
        max_shots=20,
        batch_size=5,
    )

    assert 5 <= result.syndrome_batch.shot_count <= 20
    assert result.syndrome_batch.shot_count == result.decode_result.failure_mask.shape[0]
    assert result.analysis_report.failure_count >= 1
    assert result.analysis_report.metadata["stop_reason"] == "min_failures"
    np.testing.assert_array_equal(
        result.analysis_report.logical_failure_counts,
        np.sum(
            result.decode_result.predicted_observables
            != result.decode_result.actual_observables,
            axis=0,
        ),
    )


def test_run_until_failures_owns_shot_count_when_config_has_sim_shots():
    result = run_until_failures(
        ExperimentConfig(
            code_spec=CodeSpec("repetition_code:memory", distance=3, rounds=3),
            noise_spec=NoiseModel(),
            decoder_spec={"name": "pymatching"},
            sim_spec={"shots": 100, "seed": 19},
        ),
        min_failures=1,
        max_shots=4,
        batch_size=2,
    )

    assert result.syndrome_batch.shot_count == 4
