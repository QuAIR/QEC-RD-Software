from pathlib import Path

import stim

from qec_rd.api import build_circuit, load_circuit
from qec_rd.core import CircuitSourceKind, CodeSpec, NoiseModel


def test_build_circuit_returns_generated_circuit_artifact():
    artifact = build_circuit(
        CodeSpec(family="repetition_code:memory", distance=3, rounds=3),
        NoiseModel(after_clifford_depolarization=1e-3),
    )
    assert artifact.source_kind is CircuitSourceKind.GENERATED
    assert artifact.source_format == "stim"
    assert isinstance(artifact.raw_handle, stim.Circuit)


def test_load_circuit_accepts_stim_object_and_file(tmp_path: Path):
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        distance=3,
        rounds=3,
        after_clifford_depolarization=1e-3,
    )
    object_artifact = load_circuit(circuit, format="stim")
    assert object_artifact.source_kind is CircuitSourceKind.STIM_OBJECT

    stim_path = tmp_path / "rep_d3.stim"
    stim_path.write_text(str(circuit), encoding="utf-8")
    file_artifact = load_circuit(stim_path, format="stim")
    assert file_artifact.source_kind is CircuitSourceKind.STIM_FILE
    assert file_artifact.origin_metadata["path"].endswith("rep_d3.stim")


def test_build_circuit_supports_builtin_surface_families():
    repetition = build_circuit(CodeSpec(family="repetition_code:memory", distance=3, rounds=3))
    rotated = build_circuit(CodeSpec(family="rotated_surface_code", distance=3, rounds=3))
    unrotated = build_circuit(CodeSpec(family="unrotated_surface_code", distance=3, rounds=3))

    assert isinstance(repetition.raw_handle, stim.Circuit)
    assert isinstance(rotated.raw_handle, stim.Circuit)
    assert isinstance(unrotated.raw_handle, stim.Circuit)
