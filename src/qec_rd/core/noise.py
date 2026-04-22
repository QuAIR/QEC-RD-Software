from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NoiseModel:
    # Stage 1 keeps noise limited to Stim-executable Pauli-like parameters.
    after_clifford_depolarization: float | None = None
    before_round_data_depolarization: float | None = None
    before_measure_flip_probability: float | None = None
    after_reset_flip_probability: float | None = None
