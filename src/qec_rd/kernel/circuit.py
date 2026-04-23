from __future__ import annotations

from os import PathLike

import stim

from qec_rd.adapters.stim import load_stim_circuit
from qec_rd.core import (
    CircuitArtifact,
    CircuitSourceKind,
    CodeSpec,
    NoiseModel,
    builtin_code_from_spec,
)
from qec_rd.kernel.memory import build_memory_circuit


def build_circuit(code_spec: CodeSpec, noise_model: NoiseModel | None = None) -> CircuitArtifact:
    builtin_code = builtin_code_from_spec(code_spec)
    circuit = build_memory_circuit(
        builtin_code,
        logical_basis=code_spec.logical_basis,
        rounds=code_spec.rounds,
        noise_model=noise_model,
    )
    return CircuitArtifact(
        source_kind=CircuitSourceKind.GENERATED,
        source_format="stim",
        code_spec=code_spec,
        origin_metadata={
            "builder": "platform_owned_memory_circuit",
            "code_family": builtin_code.family,
            "code_class": builtin_code.__class__.__name__,
        },
        raw_handle=circuit,
    )


def load_circuit(
    source: stim.Circuit | str | PathLike[str],
    format: str = "stim",
) -> CircuitArtifact:
    raw_handle = load_stim_circuit(source, format=format)
    if isinstance(source, stim.Circuit):
        return CircuitArtifact(
            source_kind=CircuitSourceKind.STIM_OBJECT,
            source_format="stim",
            origin_metadata={"source_type": "stim.Circuit"},
            raw_handle=raw_handle,
        )
    return CircuitArtifact(
        source_kind=CircuitSourceKind.STIM_FILE,
        source_format="stim",
        origin_metadata={"source_path": str(source)},
        raw_handle=raw_handle,
    )
