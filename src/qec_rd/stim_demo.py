"""README 技术路线中与 Stim 对齐的最小闭环：电路 → DEM 探测器事件采样。"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import stim


def repetition_code_detector_sample(
    *,
    rounds: int = 3,
    distance: int = 3,
    shots: int = 16,
    seed: int | None = 0,
    after_clifford_depolarization: float = 1e-3,
) -> npt.NDArray[np.bool_]:
    """生成重复码内存实验电路，并编译为探测器采样器做批量采样。

    对应 README 中「Stim 作为高速 stabilizer / DEM / 采样底座」的起点能力。
    默认注入极小 Clifford 退极化噪声，以便随机种子区分不同采样批次（纯噪声零电路时样本可退化）。
    """
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=rounds,
        distance=distance,
        after_clifford_depolarization=after_clifford_depolarization,
    )
    sampler = circuit.compile_detector_sampler(seed=seed)
    raw = sampler.sample(shots=shots)
    return np.asarray(raw, dtype=np.bool_)
