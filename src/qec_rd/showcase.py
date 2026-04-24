"""Acceptance-oriented showcase generation for Stage 1."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from qec_rd.api import CodeSpec, ExperimentConfig, NoiseModel, run_experiment

ACCEPTANCE_DISTANCES = (3, 5, 7)
ACCEPTANCE_DECODERS = ("pymatching",)
ACCEPTANCE_ERROR_RATES = (0.0025, 0.0035, 0.0042, 0.0050, 0.0060)
DEFAULT_SHOWCASE_SHOTS = 10_000
DEFAULT_SHOWCASE_SEED = 20260424
DEFAULT_SHOWCASE_OUTPUT_DIR = Path("docs") / "assets"
DEFAULT_SHOWCASE_BASENAME = "rotated_surface_si1000_threshold_showcase"
REFERENCE_THRESHOLD = 0.0042


@dataclass(frozen=True, slots=True)
class ShowcaseResultRow:
    distance: int
    decoder_name: str
    physical_error_rate: float
    shots: int
    seed: int
    logical_error_rate: float
    logical_error_rate_stderr: float
    failure_count: int


def build_acceptance_showcase_plan(
    *,
    shots: int = DEFAULT_SHOWCASE_SHOTS,
    seed_base: int = DEFAULT_SHOWCASE_SEED,
) -> list[dict]:
    plan: list[dict] = []
    job_index = 0
    for decoder_name in ACCEPTANCE_DECODERS:
        for distance in ACCEPTANCE_DISTANCES:
            for physical_error_rate in ACCEPTANCE_ERROR_RATES:
                plan.append(
                    {
                        "distance": distance,
                        "decoder_name": decoder_name,
                        "physical_error_rate": physical_error_rate,
                        "seed": seed_base + job_index,
                        "config": ExperimentConfig(
                            code_spec=CodeSpec(
                                family="rotated_surface_code",
                                distance=distance,
                                rounds=distance,
                                logical_basis="Z",
                            ),
                            noise_spec=NoiseModel.si1000(p=physical_error_rate),
                            decoder_spec={"name": decoder_name, "osd_order": 0},
                            sim_spec={"shots": shots, "seed": seed_base + job_index},
                        ),
                    }
                )
                job_index += 1
    return plan


def run_acceptance_showcase(
    *,
    shots: int = DEFAULT_SHOWCASE_SHOTS,
    seed_base: int = DEFAULT_SHOWCASE_SEED,
) -> list[ShowcaseResultRow]:
    rows: list[ShowcaseResultRow] = []
    for job in build_acceptance_showcase_plan(shots=shots, seed_base=seed_base):
        result = run_experiment(job["config"])
        report = result.analysis_report
        rows.append(
            ShowcaseResultRow(
                distance=job["distance"],
                decoder_name=job["decoder_name"],
                physical_error_rate=job["physical_error_rate"],
                shots=report.shot_count,
                seed=job["seed"],
                logical_error_rate=report.logical_error_rate,
                logical_error_rate_stderr=report.logical_error_rate_stderr,
                failure_count=report.failure_count,
            )
        )
    return rows


def save_acceptance_showcase(
    *,
    output_dir: str | Path = DEFAULT_SHOWCASE_OUTPUT_DIR,
    shots: int = DEFAULT_SHOWCASE_SHOTS,
    seed_base: int = DEFAULT_SHOWCASE_SEED,
) -> dict[str, Path]:
    rows = run_acceptance_showcase(shots=shots, seed_base=seed_base)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    csv_path = output_root / f"{DEFAULT_SHOWCASE_BASENAME}.csv"
    json_path = output_root / f"{DEFAULT_SHOWCASE_BASENAME}.json"
    png_path = output_root / f"{DEFAULT_SHOWCASE_BASENAME}.png"

    _write_csv(csv_path, rows)
    json_path.write_text(
        json.dumps(
            {
                "distances": list(ACCEPTANCE_DISTANCES),
                "decoders": list(ACCEPTANCE_DECODERS),
                "physical_error_rates": list(ACCEPTANCE_ERROR_RATES),
                "shots": shots,
                "seed_base": seed_base,
                "reference_threshold": REFERENCE_THRESHOLD,
                "rows": [asdict(row) for row in rows],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    _write_plot(png_path, rows, shots=shots)
    return {"csv": csv_path, "json": json_path, "png": png_path}


def _write_csv(path: Path, rows: list[ShowcaseResultRow]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _write_plot(path: Path, rows: list[ShowcaseResultRow], *, shots: int) -> None:
    decoder_titles = {
        "pymatching": "MWPM via pymatching",
        "bposd": "BP+OSD-0 via ldpc",
    }
    fig, axes = plt.subplots(
        1,
        len(ACCEPTANCE_DECODERS),
        figsize=(12, 4.8),
        sharey=True,
        constrained_layout=True,
    )
    if len(ACCEPTANCE_DECODERS) == 1:
        axes = [axes]

    for axis, decoder_name in zip(axes, ACCEPTANCE_DECODERS):
        subset = [row for row in rows if row.decoder_name == decoder_name]
        for distance in ACCEPTANCE_DISTANCES:
            distance_rows = sorted(
                [row for row in subset if row.distance == distance],
                key=lambda row: row.physical_error_rate,
            )
            x_values = [100 * row.physical_error_rate for row in distance_rows]
            y_values = [row.logical_error_rate for row in distance_rows]
            y_errors = [row.logical_error_rate_stderr for row in distance_rows]
            axis.errorbar(
                x_values,
                y_values,
                yerr=y_errors,
                marker="o",
                linewidth=1.6,
                capsize=3,
                label=f"d={distance}",
            )
        axis.axvline(
            100 * REFERENCE_THRESHOLD,
            color="0.35",
            linestyle="--",
            linewidth=1.2,
            label="ref. threshold 0.42%",
        )
        axis.set_title(decoder_titles[decoder_name])
        axis.set_xlabel("Physical error rate p (%)")
        axis.grid(alpha=0.25)

    axes[0].set_ylabel("Logical error rate")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.suptitle(
        "Rotated surface code memory showcase\nSI1000 noise, 10000 shots per point"
        if shots == DEFAULT_SHOWCASE_SHOTS
        else f"Rotated surface code memory showcase\nSI1000 noise, {shots} shots per point"
    )
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Stage 1 acceptance showcase artifacts.")
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOWCASE_SHOTS)
    parser.add_argument("--seed-base", type=int, default=DEFAULT_SHOWCASE_SEED)
    parser.add_argument("--output-dir", default=str(DEFAULT_SHOWCASE_OUTPUT_DIR))
    args = parser.parse_args()

    paths = save_acceptance_showcase(
        output_dir=args.output_dir,
        shots=args.shots,
        seed_base=args.seed_base,
    )
    print("Acceptance showcase generated:")
    for label, path in paths.items():
        print(f"  {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
