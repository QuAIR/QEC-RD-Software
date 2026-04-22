"""Decoder adaptation logic."""
from __future__ import annotations

import numpy as np
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
    if decoder_name == "custom":
        if decoder_fn is None:
            raise DecoderConfigurationError("Custom decoding requires decoder_fn.")
        result = decoder_fn(graph, batch, **kwargs)
        if not isinstance(result, DecodeResult):
            raise DecoderConfigurationError("Custom decoder must return DecodeResult.")
        return result
    raise DecoderConfigurationError(f"Unsupported decoder: {decoder_name!r}")
