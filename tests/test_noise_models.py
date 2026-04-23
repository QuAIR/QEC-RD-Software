from __future__ import annotations

from collections import Counter

from qec_rd.core import CodeSpec, NoiseModel, noise_model_from_spec
from qec_rd.core.builtin_codes import RotatedSurfaceCode
from qec_rd.kernel.circuit import build_circuit
from qec_rd.kernel.memory import build_memory_circuit


def _target_counts(circuit) -> Counter[str]:
    counts: Counter[str] = Counter()
    for instruction in circuit.flattened():
        counts[instruction.name] += len(instruction.targets_copy())
    return counts


def test_si1000_uses_scheduled_physical_noise_fields() -> None:
    noise = NoiseModel.si1000(p=0.001)

    assert noise.after_clifford_depolarization == 0.001
    assert noise.before_measure_flip_probability == 0.005
    assert noise.after_reset_flip_probability == 0.002
    assert noise.idle_depolarization == 0.0001
    assert noise.resonator_idle_depolarization == 0.002


def test_stim_circuit_level_si1000_keeps_old_coarse_preset_separate() -> None:
    coarse = NoiseModel.stim_circuit_level_si1000(p=0.001)

    assert coarse == NoiseModel(
        after_clifford_depolarization=0.001,
        before_round_data_depolarization=0.0001,
        before_measure_flip_probability=0.005,
        after_reset_flip_probability=0.002,
    )
    assert coarse != NoiseModel.si1000(p=0.001)


def test_noise_model_from_spec_distinguishes_si1000_aliases() -> None:
    assert noise_model_from_spec({"name": "SI1000Noise", "p": 0.001}) == NoiseModel.si1000(
        p=0.001
    )
    assert noise_model_from_spec({"name": "stim_circuit_level_si1000", "p": 0.001}) == (
        NoiseModel.stim_circuit_level_si1000(p=0.001)
    )


def test_scheduled_si1000_adds_idle_and_resonator_noise_to_memory_circuit() -> None:
    code = RotatedSurfaceCode(distance=3)
    scheduled = build_memory_circuit(code, "Z", 3, NoiseModel.si1000(p=0.0042))
    coarse = build_memory_circuit(
        code,
        "Z",
        3,
        NoiseModel.stim_circuit_level_si1000(p=0.0042),
    )

    scheduled_counts = _target_counts(scheduled)
    coarse_counts = _target_counts(coarse)

    assert scheduled_counts["DEPOLARIZE1"] > coarse_counts["DEPOLARIZE1"]
    assert "DEPOLARIZE1(0.0084)" in str(scheduled)


def test_scheduled_si1000_uses_compact_css_extraction_schedule() -> None:
    code = RotatedSurfaceCode(distance=3)
    scheduled = build_memory_circuit(code, "Z", 3, NoiseModel.si1000(p=0.0042))
    coarse = build_memory_circuit(
        code,
        "Z",
        3,
        NoiseModel.stim_circuit_level_si1000(p=0.0042),
    )

    scheduled_ticks = str(scheduled).splitlines().count("TICK")
    coarse_ticks = str(coarse).splitlines().count("TICK")

    assert scheduled_ticks <= 30
    assert scheduled_ticks < coarse_ticks


def test_build_circuit_records_noise_preset_metadata_without_external_names() -> None:
    artifact = build_circuit(
        CodeSpec(family="rotated_surface_code", distance=3, rounds=3),
        NoiseModel.si1000(p=0.001),
    )

    metadata_text = " ".join(str(value).lower() for value in artifact.origin_metadata.values())
    assert "deltakit" not in metadata_text
