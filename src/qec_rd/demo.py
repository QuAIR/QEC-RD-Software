"""Official end-to-end demo entry point for repository evaluation."""
from __future__ import annotations

from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, run_experiment
from qec_rd.core import ExperimentResult


def default_demo_config() -> ExperimentConfig:
    return ExperimentConfig(
        code_spec=CodeSpec(
            family="rotated_surface_code",
            distance=3,
            rounds=3,
            logical_basis="Z",
        ),
        noise_spec=NoiseModel.si1000(p=0.001),
        decoder_spec={"name": "pymatching"},
        sim_spec={"shots": 1000, "seed": 11},
    )


def run_default_demo() -> ExperimentResult:
    return run_experiment(default_demo_config())


def format_demo_summary(result: ExperimentResult) -> str:
    report = result.analysis_report
    return "\n".join(
        [
            "QEC-RD default demo completed successfully.",
            "pipeline: built-in circuit -> DEM extraction -> decoding graph -> syndrome sampling -> pymatching decode -> analysis",
            f"code_family: {result.config.code_spec.family}",
            "noise_model: si1000",
            f"decoder: {result.config.decoder_spec['name']}",
            f"shots: {report.shot_count}",
            f"logical_error_rate: {report.logical_error_rate:.6f}",
            f"failure_count: {report.failure_count}",
        ]
    )


def main() -> int:
    print(format_demo_summary(run_default_demo()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
