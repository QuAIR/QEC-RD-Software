from qec_rd.demo import format_demo_summary, run_default_demo


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
