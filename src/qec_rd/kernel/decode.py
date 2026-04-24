"""Decoder adaptation logic."""
from __future__ import annotations

import numpy as np
from ldpc import BpOsdDecoder
from pymatching import Matching

from qec_rd.core import DecodeResult, DecoderConfigurationError, DecodingGraph, SyndromeBatch


def normalize_custom_decode_result(
    *,
    decoder_name: str,
    predicted_observables: np.ndarray,
    actual_observables: np.ndarray | None,
    corrections: np.ndarray | None = None,
    metadata: dict | None = None,
) -> DecodeResult:
    if actual_observables is None:
        failure_mask = np.zeros(predicted_observables.shape[0], dtype=np.bool_)
    else:
        failure_mask = np.any(predicted_observables != actual_observables, axis=1)
    return DecodeResult(
        decoder_name=decoder_name,
        predicted_observables=np.asarray(predicted_observables, dtype=np.bool_),
        actual_observables=actual_observables,
        corrections=corrections,
        failure_mask=failure_mask,
        metadata={} if metadata is None else metadata,
    )


def _run_pymatching(graph: DecodingGraph, batch: SyndromeBatch) -> DecodeResult:
    if graph.raw_dem_handle is None:
        raise DecoderConfigurationError("pymatching decoding requires a raw DEM handle.")
    matching = Matching.from_detector_error_model(graph.raw_dem_handle)
    predictions = np.asarray(matching.decode_batch(batch.detection_events), dtype=np.bool_)
    actual = batch.observable_flips
    return normalize_custom_decode_result(
        decoder_name="pymatching",
        predicted_observables=predictions,
        actual_observables=actual,
        corrections=None,
        metadata={"backend": "pymatching"},
    )


def _run_bposd(
    graph: DecodingGraph,
    batch: SyndromeBatch,
    *,
    osd_method: str = "osd_0",
    osd_order: int = 0,
    max_iter: int = 0,
    bp_method: str = "minimum_sum",
    ms_scaling_factor: float = 1.0,
    schedule: str = "parallel",
    omp_thread_count: int = 1,
) -> DecodeResult:
    if batch.observable_flips is None:
        raise DecoderConfigurationError("bposd decoding requires observable flip data.")

    if graph.check_matrix.shape[1] == 0:
        corrections = np.zeros((batch.shot_count, 0), dtype=np.bool_)
        predictions = np.zeros_like(batch.observable_flips, dtype=np.bool_)
        return normalize_custom_decode_result(
            decoder_name="bposd",
            predicted_observables=predictions,
            actual_observables=batch.observable_flips,
            corrections=corrections,
            metadata={
                "backend": "ldpc",
                "osd_method": osd_method,
                "osd_order": osd_order,
                "converged_all": True,
                "mean_iterations": 0.0,
            },
        )

    decoder = BpOsdDecoder(
        graph.check_matrix,
        error_channel=np.asarray(graph.error_probabilities, dtype=float).tolist(),
        max_iter=max_iter,
        bp_method=bp_method,
        ms_scaling_factor=ms_scaling_factor,
        schedule=schedule,
        omp_thread_count=omp_thread_count,
        osd_method=osd_method.upper(),
        osd_order=osd_order,
    )

    corrections = np.zeros((batch.shot_count, graph.check_matrix.shape[1]), dtype=np.bool_)
    convergence_history: list[bool] = []
    iteration_history: list[int] = []
    observable_matrix_t = np.asarray(graph.observable_matrix.T, dtype=np.uint8)

    for shot_index, syndrome in enumerate(np.asarray(batch.detection_events, dtype=np.uint8)):
        decoded = decoder.decode(syndrome)
        corrections[shot_index] = np.asarray(decoded, dtype=np.bool_)
        convergence_history.append(bool(decoder.converge))
        iteration_history.append(int(decoder.iter))

    predictions = ((corrections.astype(np.uint8) @ observable_matrix_t) % 2).astype(np.bool_)
    return normalize_custom_decode_result(
        decoder_name="bposd",
        predicted_observables=predictions,
        actual_observables=batch.observable_flips,
        corrections=corrections,
        metadata={
            "backend": "ldpc",
            "osd_method": osd_method,
            "osd_order": osd_order,
            "converged_all": all(convergence_history),
            "mean_iterations": float(np.mean(iteration_history)) if iteration_history else 0.0,
        },
    )


def run_decoder(
    graph: DecodingGraph,
    batch: SyndromeBatch,
    *,
    decoder_name: str,
    decoder_fn=None,
    **kwargs,
) -> DecodeResult:
    if decoder_name == "pymatching":
        return _run_pymatching(graph, batch)
    if decoder_name in {"bposd", "ldpc", "bp_osd"}:
        return _run_bposd(graph, batch, **kwargs)
    if decoder_name == "custom":
        if decoder_fn is None:
            raise DecoderConfigurationError("Custom decoding requires decoder_fn.")
        result = decoder_fn(graph, batch, **kwargs)
        if not isinstance(result, DecodeResult):
            raise DecoderConfigurationError("Custom decoder must return DecodeResult.")
        return result
    raise DecoderConfigurationError(f"Unsupported decoder: {decoder_name!r}")
