from qec_rd.core import CodeSpec


def test_codespec_supports_stage1_builtin_code_families():
    repetition = CodeSpec(family="repetition_code:memory", distance=3, rounds=3)
    rotated = CodeSpec(family="rotated_surface_code", distance=3, rounds=3)
    unrotated = CodeSpec(family="unrotated_surface_code", distance=3, rounds=3)

    assert repetition.family == "repetition_code:memory"
    assert rotated.family == "rotated_surface_code"
    assert unrotated.family == "unrotated_surface_code"
