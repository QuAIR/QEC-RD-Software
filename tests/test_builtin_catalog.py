import pytest

from qec_rd.core.codes import CodeSpec, SUPPORTED_STAGE1_BUILTIN_FAMILIES


def test_code_spec_rejects_unknown_builtin_family() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        CodeSpec(family="unknown_family", distance=3, rounds=3)


def test_supported_stage1_builtin_families_exact_catalog() -> None:
    assert SUPPORTED_STAGE1_BUILTIN_FAMILIES == frozenset(
        {
            "repetition_code:memory",
            "rotated_surface_code",
            "unrotated_surface_code",
            "toric_code",
        }
    )
