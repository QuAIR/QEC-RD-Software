from qec_rd.demo import format_demo_summary, run_default_demo


def test_run_default_demo_returns_repetition_mwpm_result():
    result = run_default_demo()

    assert result.config.code_spec.family == "repetition_code:memory"
    assert result.config.decoder_spec["name"] == "pymatching"
    assert result.analysis_report.shot_count > 0
    assert 0.0 <= result.analysis_report.logical_error_rate <= 1.0


def test_format_demo_summary_mentions_pipeline_and_result():
    result = run_default_demo()

    summary = format_demo_summary(result)

    assert "repetition_code:memory" in summary
    assert "pymatching" in summary
    assert "logical_error_rate" in summary
    assert "pipeline" in summary.lower()
