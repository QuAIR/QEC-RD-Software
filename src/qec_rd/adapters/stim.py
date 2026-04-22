"""Stim adapter module."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import stim

from qec_rd.core import (
    CircuitArtifact,
    CircuitSourceKind,
    CodeSpec,
    DemArtifact,
    NoiseModel,
    SyndromeBatch,
    UnsupportedCircuitFormatError,
)


def _stim_generated_name(family: str) -> str:
    mapping = {
        "repetition_code:memory": "repetition_code:memory",
        "rotated_surface_code": "surface_code:rotated_memory_z",
        "unrotated_surface_code": "surface_code:unrotated_memory_z",
    }
    if family not in mapping:
        raise UnsupportedCircuitFormatError(f"Unsupported Stage 1 generated family: {family!r}")
    return mapping[family]


def build_stim_generated_circuit(code_spec: CodeSpec, noise_model: NoiseModel | None) -> stim.Circuit:
    circuit = stim.Circuit.generated(
        _stim_generated_name(code_spec.family),
        distance=code_spec.distance,
        rounds=code_spec.rounds,
        after_clifford_depolarization=noise_model.after_clifford_depolarization if noise_model else 0.0,
    )
    return circuit


def build_generated_circuit_artifact(code_spec: CodeSpec, noise_model: NoiseModel | None) -> CircuitArtifact:
    circuit = build_stim_generated_circuit(code_spec, noise_model)
    return CircuitArtifact(
        source_kind=CircuitSourceKind.GENERATED,
        source_format="stim",
        code_spec=code_spec,
        origin_metadata={"generator": "stim.Circuit.generated"},
        raw_handle=circuit,
    )


def load_stim_circuit(source: stim.Circuit | str | Path, format: str) -> CircuitArtifact:
    if format != "stim":
        raise UnsupportedCircuitFormatError(f"Unsupported circuit format: {format!r}")
    if isinstance(source, stim.Circuit):
        return CircuitArtifact(
            source_kind=CircuitSourceKind.STIM_OBJECT,
            source_format="stim",
            origin_metadata={"kind": "object"},
            raw_handle=source,
        )
    path = Path(source)
    circuit = stim.Circuit.from_file(path)
    return CircuitArtifact(
        source_kind=CircuitSourceKind.STIM_FILE,
        source_format="stim",
        origin_metadata={"path": str(path)},
        raw_handle=circuit,
    )


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
