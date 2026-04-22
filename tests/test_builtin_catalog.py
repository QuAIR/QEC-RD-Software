import pytest

from qec_rd.core import CodeSpec


def test_codespec_is_limited_to_stage1_builtin_catalog_entries():
    code = CodeSpec(
        family="rotated_surface_code",
        distance=3,
        rounds=3,
        metadata={"variant": "memory_z"},
    )

    assert code.family == "rotated_surface_code"
    assert code.metadata["variant"] == "memory_z"


def test_codespec_rejects_unknown_custom_family():
    with pytest.raises(ValueError):
        CodeSpec(family="my_custom_code", distance=3, rounds=3)
