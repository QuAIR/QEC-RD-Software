"""Circuit entry logic."""
from __future__ import annotations

from pathlib import Path

import stim

from qec_rd.adapters.stim import build_generated_circuit_artifact, load_stim_circuit
from qec_rd.core import CircuitArtifact, CodeSpec, NoiseModel


def build_circuit(code_spec: CodeSpec, noise_model: NoiseModel | None = None) -> CircuitArtifact:
    return build_generated_circuit_artifact(code_spec, noise_model)


def load_circuit(source: stim.Circuit | str | Path, format: str = "stim") -> CircuitArtifact:
    return load_stim_circuit(source, format=format)
