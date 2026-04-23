import numpy as np

from qec_rd.core import DecodeResult
from qec_rd.kernel.analysis import analyze_results


def test_analyze_results_reports_per_logical_failures_and_distribution():
    predicted = np.array(
        [
            [False, False],
            [True, False],
            [False, True],
            [True, True],
        ],
        dtype=np.bool_,
    )
    actual = np.zeros((4, 2), dtype=np.bool_)
    result = DecodeResult(
        decoder_name="custom",
        predicted_observables=predicted,
        actual_observables=actual,
        corrections=None,
        failure_mask=np.any(predicted != actual, axis=1),
    )

    report = analyze_results(result)

    np.testing.assert_array_equal(report.logical_failure_counts, np.array([2, 2]))
    np.testing.assert_allclose(report.logical_failure_rates, np.array([0.5, 0.5]))
    assert report.logical_error_distribution == {
        (False, False): 1,
        (True, False): 1,
        (False, True): 1,
        (True, True): 1,
    }
    assert report.failure_count == 3
    assert report.logical_error_rate == 0.75


def test_analyze_results_aggregates_distribution_across_batches():
    first = DecodeResult(
        decoder_name="custom",
        predicted_observables=np.array([[True, False]], dtype=np.bool_),
        actual_observables=np.array([[False, False]], dtype=np.bool_),
        corrections=None,
        failure_mask=np.array([True], dtype=np.bool_),
    )
    second = DecodeResult(
        decoder_name="custom",
        predicted_observables=np.array([[True, True], [False, False]], dtype=np.bool_),
        actual_observables=np.array([[False, False], [False, False]], dtype=np.bool_),
        corrections=None,
        failure_mask=np.array([True, False], dtype=np.bool_),
    )

    report = analyze_results([first, second])

    np.testing.assert_array_equal(report.logical_failure_counts, np.array([2, 1]))
    assert report.logical_error_distribution == {
        (False, False): 1,
        (True, False): 1,
        (False, True): 0,
        (True, True): 1,
    }
    assert report.shot_count == 3
    assert report.failure_count == 2
