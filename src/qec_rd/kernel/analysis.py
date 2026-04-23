"""Analysis logic."""
from __future__ import annotations

import math

from qec_rd.core import AnalysisReport, DecodeResult


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
    decoder_name = results[0].decoder_name if results else "unknown"
    return AnalysisReport(
        decoder_name=decoder_name,
        shot_count=shot_count,
        failure_count=failure_count,
        logical_error_rate=logical_error_rate,
        logical_error_rate_stderr=logical_error_rate_stderr,
        metadata={"num_results": len(results)},
    )
