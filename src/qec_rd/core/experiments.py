from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qec_rd.core.artifacts import CircuitArtifact
from qec_rd.core.codes import CodeSpec
from qec_rd.core.noise import NoiseModel
from qec_rd.core.results import AnalysisReport, DecodeResult, SyndromeBatch


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    code_spec: CodeSpec | dict[str, Any] | None = None
    circuit_spec: dict[str, Any] | None = None
    noise_spec: NoiseModel | dict[str, Any] = field(default_factory=dict)
    decoder_spec: dict[str, Any] = field(default_factory=dict)
    sim_spec: dict[str, Any] = field(default_factory=dict)
    analysis_spec: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    config: ExperimentConfig
    circuit: CircuitArtifact
    syndrome_batch: SyndromeBatch
    decode_result: DecodeResult
    analysis_report: AnalysisReport
