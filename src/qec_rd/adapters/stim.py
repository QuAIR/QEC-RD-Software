from __future__ import annotations

from os import PathLike
from pathlib import Path

import numpy as np
import stim

from qec_rd.core import (
    CircuitArtifact,
    DemArtifact,
    SyndromeBatch,
    UnsupportedCircuitFormatError,
)


def load_stim_circuit(
    source: stim.Circuit | str | PathLike[str],
    format: str = "stim",
) -> stim.Circuit:
    if format != "stim":
        raise UnsupportedCircuitFormatError(f"Unsupported circuit format: {format!r}")
    if isinstance(source, stim.Circuit):
        return source

    path = Path(source)
    if path.suffix.lower() != ".stim":
        raise UnsupportedCircuitFormatError(f"Unsupported circuit format: {path.suffix!r}")
    return stim.Circuit.from_file(str(path))


def extract_stim_dem(circuit_artifact: CircuitArtifact) -> DemArtifact:
    circuit = circuit_artifact.raw_handle
    dem = circuit.detector_error_model(decompose_errors=True)
    return DemArtifact(
        num_detectors=dem.num_detectors,
        num_observables=dem.num_observables,
        dem_text=str(dem),
        origin_metadata={"source_kind": circuit_artifact.source_kind.value},
        raw_handle=dem,
    )


def sample_stim_detectors(
    circuit_artifact: CircuitArtifact,
    *,
    shots: int,
    seed: int | None,
) -> SyndromeBatch:
    sampler = circuit_artifact.raw_handle.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(
        shots=shots,
        separate_observables=True,
    )
    return SyndromeBatch(
        detection_events=np.asarray(detection_events, dtype=np.bool_),
        observable_flips=np.asarray(observable_flips, dtype=np.bool_),
        measurements=None,
        shot_count=shots,
        seed=seed,
        source="stim.detector_sampler",
    )
