from __future__ import annotations

from typing import Iterable

import stim

from qec_rd.core import NoiseModel, QecRdError
from qec_rd.core.builtin_codes import BuiltinCode, RepetitionCode, StabilizerSpec


def _format_targets(targets: Iterable[int]) -> str:
    return " ".join(str(target) for target in targets)


def _append_noise_line(
    lines: list[str],
    gate: str,
    probability: float | None,
    targets: Iterable[int],
) -> None:
    target_list = list(targets)
    if probability is None or not target_list:
        return
    lines.append(f"{gate}({probability}) {_format_targets(target_list)}")


def _append_idle_noise_after_layer(
    lines: list[str],
    *,
    noise_model: NoiseModel | None,
    all_qubit_ids: Iterable[int],
    active_qubit_ids: Iterable[int],
) -> None:
    if noise_model is None or noise_model.idle_depolarization is None:
        return
    active = set(active_qubit_ids)
    idle_targets = [qubit for qubit in all_qubit_ids if qubit not in active]
    _append_noise_line(lines, "DEPOLARIZE1", noise_model.idle_depolarization, idle_targets)


def _measurement_error_gate(measure_basis: str) -> str:
    return "Z_ERROR" if measure_basis == "X" else "X_ERROR"


def _reset_gate(reset_basis: str) -> str:
    return "RX" if reset_basis == "X" else "R"


def _measure_gate(measure_basis: str) -> str:
    return "MX" if measure_basis == "X" else "M"


def _logical_support_for(code: BuiltinCode, logical_basis: str) -> tuple[tuple[int, int], ...]:
    return code.x_logical if logical_basis == "X" else code.z_logical


def _matching_stabilizers_for(
    code: BuiltinCode,
    logical_basis: str,
) -> tuple[StabilizerSpec, ...]:
    return code.x_stabilizers if logical_basis == "X" else code.z_stabilizers


def _append_stabilizer_round(
    *,
    lines: list[str],
    stabilizers: tuple[StabilizerSpec, ...],
    measure_basis: str,
    logical_basis: str,
    coord_to_qubit: dict[tuple[int, int], int],
    noise_model: NoiseModel | None,
    all_qubit_ids: tuple[int, ...],
    data_ids: tuple[int, ...],
    measurement_count: int,
    previous_measurements: dict[tuple[str, tuple[int, int]], int],
) -> int:
    if not stabilizers:
        return measurement_count

    ancilla_ids = [coord_to_qubit[stabilizer.ancilla] for stabilizer in stabilizers]
    lines.append(f"{_reset_gate(measure_basis)} {_format_targets(ancilla_ids)}")
    _append_noise_line(
        lines,
        _measurement_error_gate(measure_basis),
        None if noise_model is None else noise_model.after_reset_flip_probability,
        ancilla_ids,
    )
    lines.append("TICK")

    num_layers = len(stabilizers[0].data_path)
    for layer_index in range(num_layers):
        cx_targets: list[int] = []
        depolarize_targets: list[int] = []
        for stabilizer in stabilizers:
            data_coord = stabilizer.data_path[layer_index]
            if data_coord is None:
                continue
            ancilla_id = coord_to_qubit[stabilizer.ancilla]
            data_id = coord_to_qubit[data_coord]
            if measure_basis == "X":
                cx_targets.extend((ancilla_id, data_id))
            else:
                cx_targets.extend((data_id, ancilla_id))
            depolarize_targets.extend((ancilla_id, data_id))
        if cx_targets:
            lines.append(f"CX {_format_targets(cx_targets)}")
            _append_noise_line(
                lines,
                "DEPOLARIZE2",
                None if noise_model is None else noise_model.after_clifford_depolarization,
                depolarize_targets,
            )
            _append_idle_noise_after_layer(
                lines,
                noise_model=noise_model,
                all_qubit_ids=all_qubit_ids,
                active_qubit_ids=depolarize_targets,
            )
        lines.append("TICK")

    _append_noise_line(
        lines,
        _measurement_error_gate(measure_basis),
        None if noise_model is None else noise_model.before_measure_flip_probability,
        ancilla_ids,
    )
    lines.append(f"{_measure_gate(measure_basis)} {_format_targets(ancilla_ids)}")
    _append_noise_line(
        lines,
        "DEPOLARIZE1",
        None if noise_model is None else noise_model.resonator_idle_depolarization,
        data_ids,
    )

    start_index = measurement_count
    measurement_count += len(stabilizers)
    for offset, stabilizer in enumerate(stabilizers):
        current_index = start_index + offset
        key = (measure_basis, stabilizer.ancilla)
        previous_index = previous_measurements.get(key)
        if previous_index is not None:
            detector_terms = [
                f"rec[{current_index - measurement_count}]",
                f"rec[{previous_index - measurement_count}]",
            ]
            lines.append("DETECTOR " + " ".join(detector_terms))
        elif measure_basis == logical_basis:
            lines.append(f"DETECTOR rec[{current_index - measurement_count}]")
        previous_measurements[key] = current_index
    lines.append("TICK")
    return measurement_count


def _record_stabilizer_measurements(
    *,
    lines: list[str],
    stabilizers: tuple[StabilizerSpec, ...],
    measure_basis: str,
    logical_basis: str,
    measurement_count: int,
    previous_measurements: dict[tuple[str, tuple[int, int]], int],
) -> int:
    start_index = measurement_count
    measurement_count += len(stabilizers)
    for offset, stabilizer in enumerate(stabilizers):
        current_index = start_index + offset
        key = (measure_basis, stabilizer.ancilla)
        previous_index = previous_measurements.get(key)
        if previous_index is not None:
            detector_terms = [
                f"rec[{current_index - measurement_count}]",
                f"rec[{previous_index - measurement_count}]",
            ]
            lines.append("DETECTOR " + " ".join(detector_terms))
        elif measure_basis == logical_basis:
            lines.append(f"DETECTOR rec[{current_index - measurement_count}]")
        previous_measurements[key] = current_index
    return measurement_count


def _append_parallel_css_round(
    *,
    lines: list[str],
    code: BuiltinCode,
    logical_basis: str,
    coord_to_qubit: dict[tuple[int, int], int],
    noise_model: NoiseModel,
    all_qubit_ids: tuple[int, ...],
    data_ids: tuple[int, ...],
    measurement_count: int,
    previous_measurements: dict[tuple[str, tuple[int, int]], int],
) -> int:
    x_ancilla_ids = [coord_to_qubit[stabilizer.ancilla] for stabilizer in code.x_stabilizers]
    z_ancilla_ids = [coord_to_qubit[stabilizer.ancilla] for stabilizer in code.z_stabilizers]

    if x_ancilla_ids:
        lines.append(f"{_reset_gate('X')} {_format_targets(x_ancilla_ids)}")
        _append_noise_line(
            lines,
            _measurement_error_gate("X"),
            noise_model.after_reset_flip_probability,
            x_ancilla_ids,
        )
    if z_ancilla_ids:
        lines.append(f"{_reset_gate('Z')} {_format_targets(z_ancilla_ids)}")
        _append_noise_line(
            lines,
            _measurement_error_gate("Z"),
            noise_model.after_reset_flip_probability,
            z_ancilla_ids,
        )
    _append_noise_line(
        lines,
        "DEPOLARIZE1",
        noise_model.resonator_idle_depolarization,
        data_ids,
    )
    lines.append("TICK")

    _append_noise_line(lines, "DEPOLARIZE1", noise_model.idle_depolarization, all_qubit_ids)
    num_layers = max(
        len(code.x_stabilizers[0].data_path) if code.x_stabilizers else 0,
        len(code.z_stabilizers[0].data_path) if code.z_stabilizers else 0,
    )
    for layer_index in range(num_layers):
        cx_targets: list[int] = []
        active_targets: list[int] = []
        for stabilizer in code.x_stabilizers:
            data_coord = stabilizer.data_path[layer_index]
            if data_coord is None:
                continue
            ancilla_id = coord_to_qubit[stabilizer.ancilla]
            data_id = coord_to_qubit[data_coord]
            cx_targets.extend((ancilla_id, data_id))
            active_targets.extend((ancilla_id, data_id))
        for stabilizer in code.z_stabilizers:
            data_coord = stabilizer.data_path[layer_index]
            if data_coord is None:
                continue
            ancilla_id = coord_to_qubit[stabilizer.ancilla]
            data_id = coord_to_qubit[data_coord]
            cx_targets.extend((data_id, ancilla_id))
            active_targets.extend((ancilla_id, data_id))
        if cx_targets:
            lines.append(f"CX {_format_targets(cx_targets)}")
            _append_noise_line(
                lines,
                "DEPOLARIZE2",
                noise_model.after_clifford_depolarization,
                active_targets,
            )
            _append_idle_noise_after_layer(
                lines,
                noise_model=noise_model,
                all_qubit_ids=all_qubit_ids,
                active_qubit_ids=active_targets,
            )
        lines.append("TICK")

    _append_noise_line(
        lines,
        _measurement_error_gate("X"),
        noise_model.before_measure_flip_probability,
        x_ancilla_ids,
    )
    if x_ancilla_ids:
        lines.append(f"{_measure_gate('X')} {_format_targets(x_ancilla_ids)}")
    _append_noise_line(
        lines,
        _measurement_error_gate("Z"),
        noise_model.before_measure_flip_probability,
        z_ancilla_ids,
    )
    if z_ancilla_ids:
        lines.append(f"{_measure_gate('Z')} {_format_targets(z_ancilla_ids)}")
    _append_noise_line(
        lines,
        "DEPOLARIZE1",
        noise_model.resonator_idle_depolarization,
        data_ids,
    )

    x_start_index = measurement_count
    z_start_index = x_start_index + len(code.x_stabilizers)
    measurement_count = z_start_index + len(code.z_stabilizers)
    for measure_basis, start_index, stabilizers in (
        ("X", x_start_index, code.x_stabilizers),
        ("Z", z_start_index, code.z_stabilizers),
    ):
        for offset, stabilizer in enumerate(stabilizers):
            current_index = start_index + offset
            key = (measure_basis, stabilizer.ancilla)
            previous_index = previous_measurements.get(key)
            if previous_index is not None:
                detector_terms = [
                    f"rec[{current_index - measurement_count}]",
                    f"rec[{previous_index - measurement_count}]",
                ]
                lines.append("DETECTOR " + " ".join(detector_terms))
            elif measure_basis == logical_basis:
                lines.append(f"DETECTOR rec[{current_index - measurement_count}]")
            previous_measurements[key] = current_index
    lines.append("TICK")
    return measurement_count


def build_memory_circuit(
    code: BuiltinCode,
    logical_basis: str,
    rounds: int,
    noise_model: NoiseModel | None = None,
) -> stim.Circuit:
    if logical_basis not in {"X", "Z"}:
        raise ValueError("logical_basis must be 'X' or 'Z'")
    if rounds <= 0:
        raise ValueError("rounds must be greater than zero")
    if isinstance(code, RepetitionCode) and code.stabilizer_basis != logical_basis:
        raise QecRdError(
            "RepetitionCode must be instantiated with the same stabilizer basis "
            "as the requested logical_basis."
        )

    coord_to_qubit = {
        coord: index for index, coord in enumerate(sorted(code.all_coords))
    }
    data_coords = list(code.data_coords)
    data_ids = tuple(coord_to_qubit[coord] for coord in data_coords)
    all_qubit_ids = tuple(range(len(coord_to_qubit)))
    lines: list[str] = []

    for coord, qubit in sorted(coord_to_qubit.items(), key=lambda item: item[1]):
        lines.append(f"QUBIT_COORDS({coord[0]}, {coord[1]}) {qubit}")

    lines.append(f"{_reset_gate(logical_basis)} {_format_targets(data_ids)}")
    _append_noise_line(
        lines,
        _measurement_error_gate(logical_basis),
        None if noise_model is None else noise_model.after_reset_flip_probability,
        data_ids,
    )
    lines.append("TICK")

    measurement_count = 0
    previous_measurements: dict[tuple[str, tuple[int, int]], int] = {}
    for _ in range(rounds):
        if (
            noise_model is not None
            and noise_model.idle_depolarization is not None
            and code.x_stabilizers
            and code.z_stabilizers
        ):
            measurement_count = _append_parallel_css_round(
                lines=lines,
                code=code,
                logical_basis=logical_basis,
                coord_to_qubit=coord_to_qubit,
                noise_model=noise_model,
                all_qubit_ids=all_qubit_ids,
                data_ids=data_ids,
                measurement_count=measurement_count,
                previous_measurements=previous_measurements,
            )
        else:
            _append_noise_line(
                lines,
                "DEPOLARIZE1",
                None if noise_model is None else noise_model.before_round_data_depolarization,
                data_ids,
            )
            if lines[-1] != "TICK":
                lines.append("TICK")
            measurement_count = _append_stabilizer_round(
                lines=lines,
                stabilizers=code.x_stabilizers,
                measure_basis="X",
                logical_basis=logical_basis,
                coord_to_qubit=coord_to_qubit,
                noise_model=noise_model,
                all_qubit_ids=all_qubit_ids,
                data_ids=data_ids,
                measurement_count=measurement_count,
                previous_measurements=previous_measurements,
            )
            measurement_count = _append_stabilizer_round(
                lines=lines,
                stabilizers=code.z_stabilizers,
                measure_basis="Z",
                logical_basis=logical_basis,
                coord_to_qubit=coord_to_qubit,
                noise_model=noise_model,
                all_qubit_ids=all_qubit_ids,
                data_ids=data_ids,
                measurement_count=measurement_count,
                previous_measurements=previous_measurements,
            )

    _append_noise_line(
        lines,
        _measurement_error_gate(logical_basis),
        None if noise_model is None else noise_model.before_measure_flip_probability,
        data_ids,
    )
    lines.append(f"{_measure_gate(logical_basis)} {_format_targets(data_ids)}")
    final_start_index = measurement_count
    measurement_count += len(data_ids)
    data_measurement_index = {
        coord: final_start_index + index for index, coord in enumerate(data_coords)
    }

    for stabilizer in _matching_stabilizers_for(code, logical_basis):
        previous_index = previous_measurements[(logical_basis, stabilizer.ancilla)]
        detector_terms = [f"rec[{previous_index - measurement_count}]"]
        detector_terms.extend(
            f"rec[{data_measurement_index[coord] - measurement_count}]"
            for coord in stabilizer.support
        )
        lines.append("DETECTOR " + " ".join(detector_terms))

    for coord in _logical_support_for(code, logical_basis):
        lines.append(
            f"OBSERVABLE_INCLUDE(0) rec[{data_measurement_index[coord] - measurement_count}]"
        )

    return stim.Circuit("\n".join(lines) + "\n")
