import numpy as np

from qec_rd.stim_demo import repetition_code_detector_sample


def test_repetition_code_detector_sample_shape_dtype_and_determinism():
    # 退极化极弱时单次少量 shot 常全为 False；提高噪声以便断言「不同种子」产生不同批次。
    p = 0.05
    a = repetition_code_detector_sample(
        shots=12, seed=7, after_clifford_depolarization=p
    )
    b = repetition_code_detector_sample(
        shots=12, seed=7, after_clifford_depolarization=p
    )
    assert a.dtype == np.bool_
    assert a.shape == (12, a.shape[1])
    assert np.array_equal(a, b)

    c = repetition_code_detector_sample(
        shots=12, seed=8, after_clifford_depolarization=p
    )
    assert not np.array_equal(a, c)
