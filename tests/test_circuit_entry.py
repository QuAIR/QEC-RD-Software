from pathlib import Path

import pytest
import stim

from qec_rd.core import (
    CircuitSourceKind,
    CodeSpec,
    ExperimentConfig,
    NoiseModel,
    RepetitionCode,
    RotatedSurfaceCode,
    ToricCode,
    UnrotatedSurfaceCode,
    UnsupportedCircuitFormatError,
    builtin_code_from_spec,
)
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.memory import build_memory_circuit
from qec_rd.kernel.runner import ExperimentRunner


def test_build_circuit_returns_generated_artifact_for_supported_families() -> None:
    for family in (
        "repetition_code:memory",
        "rotated_surface_code",
        "unrotated_surface_code",
        "toric_code",
    ):
        artifact = build_circuit(
            CodeSpec(family=family, distance=3, rounds=3),
            NoiseModel(after_clifford_depolarization=1e-3),
        )

        assert artifact.source_kind == CircuitSourceKind.GENERATED
        assert artifact.source_format == "stim"
        assert artifact.code_spec is not None
        assert isinstance(artifact.raw_handle, stim.Circuit)
        assert artifact.origin_metadata["builder"] == "platform_owned_memory_circuit"
        artifact.raw_handle.detector_error_model()


def test_load_circuit_accepts_stim_object_and_stim_file(tmp_path: Path) -> None:
    circuit = stim.Circuit("H 0\nM 0\n")

    object_artifact = load_circuit(circuit)
    assert object_artifact.source_kind == CircuitSourceKind.STIM_OBJECT
    assert object_artifact.raw_handle is circuit

    path = tmp_path / "example.stim"
    path.write_text(str(circuit), encoding="utf-8")

    file_artifact = load_circuit(path, format="stim")
    assert file_artifact.source_kind == CircuitSourceKind.STIM_FILE
    assert isinstance(file_artifact.raw_handle, stim.Circuit)


def test_load_circuit_rejects_unsupported_format_for_stim_object() -> None:
    circuit = stim.Circuit("H 0\nM 0\n")

    with pytest.raises(UnsupportedCircuitFormatError):
        load_circuit(circuit, format="qasm")


def test_builtin_code_factory_returns_platform_owned_classes() -> None:
    assert isinstance(
        builtin_code_from_spec(CodeSpec("repetition_code:memory", 3, 2)),
        RepetitionCode,
    )
    assert isinstance(
        builtin_code_from_spec(CodeSpec("rotated_surface_code", 3, 2)),
        RotatedSurfaceCode,
    )
    assert isinstance(
        builtin_code_from_spec(CodeSpec("unrotated_surface_code", 3, 2)),
        UnrotatedSurfaceCode,
    )
    assert isinstance(
        builtin_code_from_spec(CodeSpec("toric_code", 3, 2)),
        ToricCode,
    )


def test_build_memory_circuit_uses_basis_as_experiment_choice_on_same_surface_code() -> None:
    code = RotatedSurfaceCode(distance=3)

    z_memory = build_memory_circuit(code, logical_basis="Z", rounds=2)
    x_memory = build_memory_circuit(code, logical_basis="X", rounds=2)

    z_text = str(z_memory)
    x_text = str(x_memory)

    assert "surface_code:rotated_memory_z" not in z_text
    assert "surface_code:rotated_memory_z" not in x_text
    assert "\nM " in z_text
    assert "\nMX " in x_text
    assert z_text != x_text


def test_toy_phenomenological_noise_generates_data_and_measurement_noise() -> None:
    circuit = build_circuit(
        CodeSpec(family="rotated_surface_code", distance=3, rounds=2),
        NoiseModel.toy_phenomenological(p=0.01, p_measurement_flip=0.02),
    ).raw_handle

    circuit_text = str(circuit)
    assert "DEPOLARIZE1(0.01)" in circuit_text
    assert "X_ERROR(0.02)" in circuit_text or "Z_ERROR(0.02)" in circuit_text
    assert "DEPOLARIZE2" not in circuit_text
    circuit.detector_error_model()


def test_runner_prepare_accepts_named_noise_spec_dict() -> None:
    circuit, graph = ExperimentRunner().prepare(
        ExperimentConfig(
            code_spec=CodeSpec(family="rotated_surface_code", distance=3, rounds=2),
            noise_spec={"name": "si1000", "p": 0.01},
        )
    )

    assert "DEPOLARIZE2(0.01)" in str(circuit.raw_handle)
    assert graph.num_detectors > 0
