from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class NoiseModel:
    # Stage 1 keeps noise limited to Stim-executable Pauli-like parameters.
    after_clifford_depolarization: float | None = None
    before_round_data_depolarization: float | None = None
    before_measure_flip_probability: float | None = None
    after_reset_flip_probability: float | None = None
    idle_depolarization: float | None = None
    resonator_idle_depolarization: float | None = None

    @classmethod
    def toy(
        cls,
        p: float = 0.0,
        p_measurement_flip: float | None = None,
    ) -> NoiseModel:
        """Deltakit-style toy preset, projected onto Stage 1 Stim channels."""
        measurement_flip = p if p_measurement_flip is None else p_measurement_flip
        return cls(
            after_clifford_depolarization=p,
            before_round_data_depolarization=p / 10,
            before_measure_flip_probability=measurement_flip,
            after_reset_flip_probability=p / 10,
        )

    @classmethod
    def toy_phenomenological(
        cls,
        p: float = 0.0,
        p_measurement_flip: float | None = None,
    ) -> NoiseModel:
        """Phenomenological idle/data noise plus measurement flips."""
        measurement_flip = p if p_measurement_flip is None else p_measurement_flip
        return cls(
            before_round_data_depolarization=p,
            before_measure_flip_probability=measurement_flip,
        )

    @classmethod
    def sd6(cls, p: float = 0.0) -> NoiseModel:
        """SD6 preset with one shared Pauli-like error probability."""
        return cls(
            after_clifford_depolarization=p,
            before_round_data_depolarization=p,
            before_measure_flip_probability=p,
            after_reset_flip_probability=p,
        )

    @classmethod
    def stim_circuit_level_si1000(cls, p: float = 0.0, pL: float = 0.0) -> NoiseModel:
        """Coarse Stim circuit-level SI1000-style preset without scheduled idles."""
        if pL != 0:
            raise ValueError("SI1000 leakage parameter pL is non-Pauli and out of Stage 1 scope.")
        return cls(
            after_clifford_depolarization=p,
            before_round_data_depolarization=p / 10,
            before_measure_flip_probability=5 * p,
            after_reset_flip_probability=2 * p,
        )

    @classmethod
    def si1000(cls, p: float = 0.0, pL: float = 0.0) -> NoiseModel:
        """Scheduled superconducting-inspired SI1000 preset without leakage."""
        if pL != 0:
            raise ValueError("SI1000 leakage parameter pL is non-Pauli and out of Stage 1 scope.")
        return cls(
            after_clifford_depolarization=p,
            before_measure_flip_probability=5 * p,
            after_reset_flip_probability=2 * p,
            idle_depolarization=p / 10,
            resonator_idle_depolarization=2 * p,
        )


_PRESET_ALIASES = {
    "toy": "toy",
    "toy_noise": "toy",
    "toynoise": "toy",
    "toy_phenomenological": "toy_phenomenological",
    "toy_phenomenological_noise": "toy_phenomenological",
    "toyphenomenologicalnoise": "toy_phenomenological",
    "sd6": "sd6",
    "sd6_noise": "sd6",
    "sd6noise": "sd6",
    "si1000": "si1000",
    "si1000_noise": "si1000",
    "si1000noise": "si1000",
    "stim_circuit_level_si1000": "stim_circuit_level_si1000",
    "stimcircuitlevelsi1000": "stim_circuit_level_si1000",
    "stim_si1000": "stim_circuit_level_si1000",
    "stimsi1000": "stim_circuit_level_si1000",
}


def _normalize_preset_name(name: object) -> str:
    return str(name).strip().lower().replace("-", "_").replace(" ", "_")


def noise_model_from_spec(spec: NoiseModel | Mapping[str, Any] | None) -> NoiseModel | None:
    if spec is None or isinstance(spec, NoiseModel):
        return spec

    data = dict(spec)
    name = data.pop("name", None)
    if name is None:
        name = data.pop("model", None)
    if name is None:
        return NoiseModel(**data)

    normalized_name = _normalize_preset_name(name)
    preset_name = _PRESET_ALIASES.get(normalized_name) or _PRESET_ALIASES.get(
        normalized_name.replace("_", "")
    )
    if preset_name is None:
        supported = ", ".join(sorted(_PRESET_ALIASES))
        raise ValueError(f"Unsupported noise model preset '{name}'. Supported presets: {supported}.")
    preset = getattr(NoiseModel, preset_name)
    return preset(**data)
