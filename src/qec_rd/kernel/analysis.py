"""Analysis logic."""
from __future__ import annotations

from itertools import product
import math

import numpy as np

from qec_rd.core import AnalysisReport, DecodeResult


def _logical_error_events(results: list[DecodeResult]) -> np.ndarray:
    events = []
    for result in results:
        if result.actual_observables is None:
            continue
        predicted = np.asarray(result.predicted_observables, dtype=np.bool_)
        actual = np.asarray(result.actual_observables, dtype=np.bool_)
        events.append(predicted != actual)
    if not events:
        return np.zeros((0, 0), dtype=np.bool_)
    return np.vstack(events)


def _logical_error_distribution(events: np.ndarray) -> dict[tuple[bool, ...], int]:
    if events.shape[1] == 0:
        return {}

    distribution = {
        tuple(pattern): 0 for pattern in product((False, True), repeat=events.shape[1])
    }
    for row in events:
        key = tuple(bool(item) for item in row)
        distribution[key] += 1
    return distribution


def analyze_results(result: DecodeResult | list[DecodeResult]) -> AnalysisReport:
    results = [result] if isinstance(result, DecodeResult) else result
    shot_count = sum(item.failure_mask.shape[0] for item in results)
    failure_count = sum(item.failure_count for item in results)
    logical_error_rate = failure_count / shot_count if shot_count else 0.0
    logical_error_rate_stderr = (
        math.sqrt(logical_error_rate * (1.0 - logical_error_rate) / shot_count)
        if shot_count
        else 0.0
    )
    logical_events = _logical_error_events(results)
    logical_failure_counts = (
        np.sum(logical_events, axis=0, dtype=np.int64)
        if logical_events.size
        else np.zeros(0, dtype=np.int64)
    )
    logical_failure_rates = (
        logical_failure_counts / logical_events.shape[0]
        if logical_events.shape[0]
        else np.zeros(0, dtype=np.float64)
    )
    decoder_name = results[0].decoder_name if results else "unknown"
    return AnalysisReport(
        decoder_name=decoder_name,
        shot_count=shot_count,
        failure_count=failure_count,
        logical_error_rate=logical_error_rate,
        logical_error_rate_stderr=logical_error_rate_stderr,
        logical_failure_counts=logical_failure_counts,
        logical_failure_rates=logical_failure_rates,
        logical_error_distribution=_logical_error_distribution(logical_events),
        metadata={
            "num_results": len(results),
            "logical_event_count": int(logical_events.shape[0]),
        },
    )
