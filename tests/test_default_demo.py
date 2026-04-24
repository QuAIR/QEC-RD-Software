from unittest.mock import MagicMock, patch

import pytest

from qec_rd.demo import format_demo_summary, main, run_default_demo


def test_run_default_demo_returns_rotated_surface_mwpm_result():
    result = run_default_demo()

    assert result.config.code_spec.family == "rotated_surface_code"
    assert result.config.decoder_spec["name"] == "pymatching"
    assert result.analysis_report.shot_count == 1000
    assert 0.0 <= result.analysis_report.logical_error_rate <= 1.0


def test_format_demo_summary_mentions_pipeline_and_result():
    result = run_default_demo()

    summary = format_demo_summary(result)

    assert "rotated_surface_code" in summary
    assert "pymatching" in summary
    assert "1000" in summary
    assert "logical_error_rate" in summary
    assert "pipeline" in summary.lower()


def test_main_prints_summary_and_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("qec_rd.demo.run_default_demo") as mock_run:
        mock_result = MagicMock()
        mock_result.config.code_spec.family = "rotated_surface_code"
        mock_result.config.decoder_spec = {"name": "pymatching"}
        mock_result.analysis_report.shot_count = 1000
        mock_result.analysis_report.logical_error_rate = 0.001
        mock_result.analysis_report.failure_count = 1
        mock_run.return_value = mock_result

        rc = main()

    assert rc == 0
    captured = capsys.readouterr()
    assert "QEC-RD default demo completed successfully" in captured.out
    assert "rotated_surface_code" in captured.out
