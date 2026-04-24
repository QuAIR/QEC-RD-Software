from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from qec_rd.showcase import (
    ACCEPTANCE_DECODERS,
    ACCEPTANCE_DISTANCES,
    ACCEPTANCE_ERROR_RATES,
    DEFAULT_SHOWCASE_BASENAME,
    DEFAULT_SHOWCASE_OUTPUT_DIR,
    DEFAULT_SHOWCASE_SEED,
    DEFAULT_SHOWCASE_SHOTS,
    REFERENCE_THRESHOLD,
    ShowcaseResultRow,
    _write_csv,
    _write_plot,
    build_acceptance_showcase_plan,
    main,
    run_acceptance_showcase,
    save_acceptance_showcase,
)


def test_acceptance_showcase_plan_covers_all_distances_decoders_and_error_rates() -> None:
    plan = build_acceptance_showcase_plan()

    assert len(plan) == (
        len(ACCEPTANCE_DISTANCES)
        * len(ACCEPTANCE_DECODERS)
        * len(ACCEPTANCE_ERROR_RATES)
    )
    assert {job["distance"] for job in plan} == set(ACCEPTANCE_DISTANCES)
    assert {job["decoder_name"] for job in plan} == set(ACCEPTANCE_DECODERS)
    assert {job["physical_error_rate"] for job in plan} == set(ACCEPTANCE_ERROR_RATES)


def test_acceptance_showcase_plan_uses_requested_shot_budget() -> None:
    plan = build_acceptance_showcase_plan(shots=10_000)

    assert all(job["config"].sim_spec["shots"] == 10_000 for job in plan)


def test_acceptance_showcase_plan_uses_incrementing_seeds() -> None:
    plan = build_acceptance_showcase_plan(seed_base=100)

    seeds = [job["seed"] for job in plan]
    assert seeds == list(range(100, 100 + len(plan)))


def _make_fake_report(logical_error_rate: float = 0.01, failure_count: int = 10) -> MagicMock:
    report = MagicMock()
    report.shot_count = 100
    report.logical_error_rate = logical_error_rate
    report.logical_error_rate_stderr = 0.001
    report.failure_count = failure_count
    return report


def test_run_acceptance_showcase_returns_rows_for_all_jobs() -> None:
    fake_report = _make_fake_report()
    fake_result = MagicMock()
    fake_result.analysis_report = fake_report

    with patch("qec_rd.showcase.run_experiment", return_value=fake_result):
        rows = run_acceptance_showcase()

    expected_count = len(ACCEPTANCE_DISTANCES) * len(ACCEPTANCE_DECODERS) * len(ACCEPTANCE_ERROR_RATES)
    assert len(rows) == expected_count
    for row in rows:
        assert isinstance(row, ShowcaseResultRow)
        assert row.logical_error_rate == 0.01
        assert row.failure_count == 10


def test_run_acceptance_showcase_respects_custom_shots_and_seed() -> None:
    fake_report = _make_fake_report()
    fake_report.shot_count = 500
    fake_result = MagicMock()
    fake_result.analysis_report = fake_report

    with patch("qec_rd.showcase.run_experiment", return_value=fake_result):
        rows = run_acceptance_showcase(shots=500, seed_base=7)

    assert all(row.shots == 500 for row in rows)
    assert all(row.seed >= 7 for row in rows)


def test_save_acceptance_showcase_writes_csv_json_and_png(tmp_path: Path) -> None:
    rows = [
        ShowcaseResultRow(
            distance=3,
            decoder_name="pymatching",
            physical_error_rate=0.001,
            shots=10,
            seed=1,
            logical_error_rate=0.01,
            logical_error_rate_stderr=0.001,
            failure_count=1,
        )
    ]

    with patch("qec_rd.showcase.run_acceptance_showcase", return_value=rows):
        paths = save_acceptance_showcase(output_dir=tmp_path)

    assert paths["csv"].exists()
    assert paths["json"].exists()
    assert paths["png"].exists()

    csv_text = paths["csv"].read_text(encoding="utf-8")
    assert "distance" in csv_text
    assert "pymatching" in csv_text

    data = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert data["distances"] == list(ACCEPTANCE_DISTANCES)
    assert data["decoders"] == list(ACCEPTANCE_DECODERS)
    assert data["physical_error_rates"] == list(ACCEPTANCE_ERROR_RATES)
    assert data["shots"] == DEFAULT_SHOWCASE_SHOTS
    assert data["seed_base"] == DEFAULT_SHOWCASE_SEED
    assert data["reference_threshold"] == REFERENCE_THRESHOLD
    assert len(data["rows"]) == 1


def test_write_csv_creates_valid_csv(tmp_path: Path) -> None:
    rows = [
        ShowcaseResultRow(
            distance=3,
            decoder_name="pymatching",
            physical_error_rate=0.001,
            shots=10,
            seed=1,
            logical_error_rate=0.01,
            logical_error_rate_stderr=0.001,
            failure_count=1,
        ),
        ShowcaseResultRow(
            distance=5,
            decoder_name="pymatching",
            physical_error_rate=0.002,
            shots=10,
            seed=2,
            logical_error_rate=0.02,
            logical_error_rate_stderr=0.002,
            failure_count=2,
        ),
    ]
    path = tmp_path / "test.csv"
    _write_csv(path, rows)

    text = path.read_text(encoding="utf-8")
    lines = text.strip().split("\n")
    assert len(lines) == 3  # header + 2 rows
    assert "distance" in lines[0]
    assert "pymatching" in lines[1]


def test_write_plot_creates_png_file(tmp_path: Path) -> None:
    rows = [
        ShowcaseResultRow(
            distance=d,
            decoder_name="pymatching",
            physical_error_rate=p,
            shots=10,
            seed=1,
            logical_error_rate=0.01 * d,
            logical_error_rate_stderr=0.001,
            failure_count=1,
        )
        for d in ACCEPTANCE_DISTANCES
        for p in ACCEPTANCE_ERROR_RATES
    ]
    path = tmp_path / "test.png"
    _write_plot(path, rows, shots=DEFAULT_SHOWCASE_SHOTS)

    assert path.exists()
    assert path.stat().st_size > 0


def test_write_plot_uses_custom_shots_in_title(tmp_path: Path) -> None:
    rows = [
        ShowcaseResultRow(
            distance=d,
            decoder_name="pymatching",
            physical_error_rate=p,
            shots=10,
            seed=1,
            logical_error_rate=0.01 * d,
            logical_error_rate_stderr=0.001,
            failure_count=1,
        )
        for d in ACCEPTANCE_DISTANCES
        for p in ACCEPTANCE_ERROR_RATES
    ]
    path = tmp_path / "test.png"
    _write_plot(path, rows, shots=500)

    assert path.exists()


def test_main_runs_and_prints_paths(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    with (
        patch("qec_rd.showcase.save_acceptance_showcase") as mock_save,
        patch.object(sys, "argv", ["qec-rd-showcase", "--output-dir", str(tmp_path)]),
    ):
        mock_save.return_value = {
            "csv": tmp_path / "out.csv",
            "json": tmp_path / "out.json",
            "png": tmp_path / "out.png",
        }
        rc = main()

    assert rc == 0
    captured = capsys.readouterr()
    assert "Acceptance showcase generated:" in captured.out
    assert "csv:" in captured.out


def test_main_with_custom_args(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    with (
        patch("qec_rd.showcase.save_acceptance_showcase") as mock_save,
        patch.object(sys, "argv", [
            "qec-rd-showcase",
            "--shots", "500",
            "--seed-base", "42",
            "--output-dir", str(tmp_path),
        ]),
    ):
        mock_save.return_value = {
            "csv": tmp_path / "out.csv",
            "json": tmp_path / "out.json",
            "png": tmp_path / "out.png",
        }
        rc = main()

    assert rc == 0
    mock_save.assert_called_once_with(
        output_dir=str(tmp_path),
        shots=500,
        seed_base=42,
    )
