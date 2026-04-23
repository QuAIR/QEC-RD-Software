import pytest

from qec_rd.core.builtin_codes import RotatedSurfaceCode
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


def test_rotated_surface_uses_hook_safe_x_and_z_stabilizer_orders() -> None:
    code = RotatedSurfaceCode(distance=3)

    assert code.x_stabilizers[0].data_path == (None, None, (1, 3), (1, 1))
    assert code.z_stabilizers[2].data_path == ((3, 1), (5, 1), None, None)
