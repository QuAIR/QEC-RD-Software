import pytest

from qec_rd.core.codes import CodeSpec


@pytest.mark.parametrize(
    "family",
    [
        "repetition_code:memory",
        "rotated_surface_code",
        "unrotated_surface_code",
        "toric_code",
    ],
)
def test_code_spec_accepts_supported_stage1_builtin_families(family: str) -> None:
    code = CodeSpec(family=family, distance=3, rounds=3)

    assert code.family == family
