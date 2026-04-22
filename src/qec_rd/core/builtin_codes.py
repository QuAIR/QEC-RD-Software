from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qec_rd.core.codes import CodeSpec

Coord = tuple[int, int]


def _sorted_coords(coords: Iterable[Coord]) -> tuple[Coord, ...]:
    return tuple(sorted(coords))


def _wrap(coord: Coord, *, width: int, height: int) -> Coord:
    return (coord[0] % width, coord[1] % height)


@dataclass(frozen=True, slots=True)
class StabilizerSpec:
    basis: str
    ancilla: Coord
    data_path: tuple[Coord | None, ...]

    def __post_init__(self) -> None:
        if self.basis not in {"X", "Z"}:
            raise ValueError("stabilizer basis must be 'X' or 'Z'")

    @property
    def support(self) -> tuple[Coord, ...]:
        return tuple(coord for coord in self.data_path if coord is not None)


class BuiltinCode:
    __slots__ = (
        "family",
        "distance",
        "data_coords",
        "x_ancilla_coords",
        "z_ancilla_coords",
        "x_stabilizers",
        "z_stabilizers",
        "x_logical",
        "z_logical",
    )

    def __init__(
        self,
        *,
        family: str,
        distance: int,
        data_coords: tuple[Coord, ...],
        x_ancilla_coords: tuple[Coord, ...],
        z_ancilla_coords: tuple[Coord, ...],
        x_stabilizers: tuple[StabilizerSpec, ...],
        z_stabilizers: tuple[StabilizerSpec, ...],
        x_logical: tuple[Coord, ...],
        z_logical: tuple[Coord, ...],
    ) -> None:
        if distance <= 0:
            raise ValueError("distance must be greater than zero")
        self.family = family
        self.distance = distance
        self.data_coords = data_coords
        self.x_ancilla_coords = x_ancilla_coords
        self.z_ancilla_coords = z_ancilla_coords
        self.x_stabilizers = x_stabilizers
        self.z_stabilizers = z_stabilizers
        self.x_logical = x_logical
        self.z_logical = z_logical

    @property
    def all_coords(self) -> tuple[Coord, ...]:
        return _sorted_coords(
            self.data_coords + self.x_ancilla_coords + self.z_ancilla_coords
        )


class RepetitionCode(BuiltinCode):
    def __init__(self, distance: int, stabilizer_basis: str = "Z") -> None:
        if stabilizer_basis not in {"X", "Z"}:
            raise ValueError("stabilizer_basis must be 'X' or 'Z'")
        data_coords = _sorted_coords((2 * index, 0) for index in range(distance))
        ancillas = _sorted_coords((2 * index + 1, 0) for index in range(distance - 1))
        stabilizers = tuple(
            StabilizerSpec(
                basis=stabilizer_basis,
                ancilla=ancilla,
                data_path=((ancilla[0] - 1, 0), (ancilla[0] + 1, 0)),
            )
            for ancilla in ancillas
        )
        super().__init__(
            family="repetition_code:memory",
            distance=distance,
            data_coords=data_coords,
            x_ancilla_coords=ancillas if stabilizer_basis == "X" else (),
            z_ancilla_coords=ancillas if stabilizer_basis == "Z" else (),
            x_stabilizers=stabilizers if stabilizer_basis == "X" else (),
            z_stabilizers=stabilizers if stabilizer_basis == "Z" else (),
            x_logical=data_coords,
            z_logical=(data_coords[0],),
        )
        self.stabilizer_basis = stabilizer_basis


class UnrotatedSurfaceCode(BuiltinCode):
    def __init__(self, distance: int) -> None:
        size = 2 * distance - 1
        data_coords = _sorted_coords(
            (x, y)
            for x in range(size)
            for y in range(size)
            if (x % 2) == (y % 2)
        )
        x_ancillas = _sorted_coords(
            (x, y)
            for x in range(size)
            for y in range(size)
            if (x % 2) == 0 and (y % 2) == 1
        )
        z_ancillas = _sorted_coords(
            (x, y)
            for x in range(size)
            for y in range(size)
            if (x % 2) == 1 and (y % 2) == 0
        )
        deltas = ((0, 1), (1, 0), (0, -1), (-1, 0))
        data_set = set(data_coords)

        def build_stabilizers(
            ancillas: tuple[Coord, ...],
            basis: str,
        ) -> tuple[StabilizerSpec, ...]:
            return tuple(
                StabilizerSpec(
                    basis=basis,
                    ancilla=ancilla,
                    data_path=tuple(
                        coord if coord in data_set else None
                        for coord in (
                            (ancilla[0] + dx, ancilla[1] + dy) for dx, dy in deltas
                        )
                    ),
                )
                for ancilla in ancillas
            )

        x_logical = tuple((x, size - 1) for x in range(0, size, 2))
        z_logical = tuple((0, y) for y in range(0, size, 2))
        super().__init__(
            family="unrotated_surface_code",
            distance=distance,
            data_coords=data_coords,
            x_ancilla_coords=x_ancillas,
            z_ancilla_coords=z_ancillas,
            x_stabilizers=build_stabilizers(x_ancillas, "X"),
            z_stabilizers=build_stabilizers(z_ancillas, "Z"),
            x_logical=x_logical,
            z_logical=z_logical,
        )


class RotatedSurfaceCode(BuiltinCode):
    def __init__(self, distance: int) -> None:
        max_coord = 2 * distance
        data_coords = _sorted_coords(
            (x, y)
            for x in range(1, max_coord, 2)
            for y in range(1, max_coord, 2)
        )
        x_ancillas = _sorted_coords(
            (x, y)
            for x in range(0, max_coord + 1, 2)
            for y in range(2, max_coord - 1, 2)
            if (x + y - max_coord) % 4 == 0
        )
        z_ancillas = _sorted_coords(
            (x, y)
            for x in range(2, max_coord - 1, 2)
            for y in range(0, max_coord + 1, 2)
            if (x + y - max_coord) % 4 == 2
        )
        deltas = ((-1, 1), (1, 1), (-1, -1), (1, -1))
        data_set = set(data_coords)

        def build_stabilizers(
            ancillas: tuple[Coord, ...],
            basis: str,
        ) -> tuple[StabilizerSpec, ...]:
            return tuple(
                StabilizerSpec(
                    basis=basis,
                    ancilla=ancilla,
                    data_path=tuple(
                        coord if coord in data_set else None
                        for coord in (
                            (ancilla[0] + dx, ancilla[1] + dy) for dx, dy in deltas
                        )
                    ),
                )
                for ancilla in ancillas
            )

        x_logical = tuple((x, max_coord - 1) for x in range(1, max_coord, 2))
        z_logical = tuple((1, y) for y in range(1, max_coord, 2))
        super().__init__(
            family="rotated_surface_code",
            distance=distance,
            data_coords=data_coords,
            x_ancilla_coords=x_ancillas,
            z_ancilla_coords=z_ancillas,
            x_stabilizers=build_stabilizers(x_ancillas, "X"),
            z_stabilizers=build_stabilizers(z_ancillas, "Z"),
            x_logical=x_logical,
            z_logical=z_logical,
        )


class ToricCode(BuiltinCode):
    def __init__(self, distance: int) -> None:
        width = 2 * distance
        height = 2 * distance
        data_coords = _sorted_coords(
            list(
                (x, y)
                for x in range(0, width - 1, 2)
                for y in range(0, height - 1, 2)
            )
            + list(
                (x, y)
                for x in range(1, width, 2)
                for y in range(1, height, 2)
            )
        )
        x_ancillas = _sorted_coords(
            (x, y)
            for x in range(0, width - 1, 2)
            for y in range(1, height, 2)
        )
        z_ancillas = _sorted_coords(
            (x, y)
            for x in range(1, width, 2)
            for y in range(0, height - 1, 2)
        )
        deltas = ((0, 1), (1, 0), (0, -1), (-1, 0))

        def build_stabilizers(
            ancillas: tuple[Coord, ...],
            basis: str,
        ) -> tuple[StabilizerSpec, ...]:
            return tuple(
                StabilizerSpec(
                    basis=basis,
                    ancilla=ancilla,
                    data_path=tuple(
                        _wrap(
                            (ancilla[0] + dx, ancilla[1] + dy),
                            width=width,
                            height=height,
                        )
                        for dx, dy in deltas
                    ),
                )
                for ancilla in ancillas
            )

        x_logical = tuple((x, 0) for x in range(0, width - 1, 2))
        z_logical = tuple((0, y) for y in range(0, height - 1, 2))
        super().__init__(
            family="toric_code",
            distance=distance,
            data_coords=data_coords,
            x_ancilla_coords=x_ancillas,
            z_ancilla_coords=z_ancillas,
            x_stabilizers=build_stabilizers(x_ancillas, "X"),
            z_stabilizers=build_stabilizers(z_ancillas, "Z"),
            x_logical=x_logical,
            z_logical=z_logical,
        )


def builtin_code_from_spec(code_spec: CodeSpec) -> BuiltinCode:
    if code_spec.family == "repetition_code:memory":
        return RepetitionCode(
            distance=code_spec.distance,
            stabilizer_basis=code_spec.logical_basis,
        )
    if code_spec.family == "rotated_surface_code":
        return RotatedSurfaceCode(distance=code_spec.distance)
    if code_spec.family == "unrotated_surface_code":
        return UnrotatedSurfaceCode(distance=code_spec.distance)
    if code_spec.family == "toric_code":
        return ToricCode(distance=code_spec.distance)
    raise ValueError(f"unsupported built-in family: {code_spec.family}")
