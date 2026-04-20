# QEC-RD Phase 0：Python 包与 Stim 底座 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 README 中的平台愿景落地为可安装、可测试、可 CI 的 **Phase 0 交付物**：根目录 Python 包、`stim` 驱动的最小 DEM 探测器采样闭环、架构对照文档；Tensor QEC / DeltaKit 深度集成留作后续 Epic。

**Architecture:** 采用 **src layout**（`src/qec_rd/`），依赖 **PyPI `stim` + `numpy`**；第一个对外能力为重复码内存电路的探测器事件批量采样，验证「电路 → `compile_detector_sampler` → `sample`」路径。GitHub Actions 在多版本 Python 上运行 `pytest`。

**Tech Stack:** Python ≥3.10、`setuptools`、`pytest`、`numpy`、`stim`。

---

## 文件结构（本阶段）

| 路径 | 职责 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖、`pytest` 配置、`setuptools` 包发现（`where = ["src"]`） |
| `src/qec_rd/__init__.py` | 包入口与 `__version__` |
| `src/qec_rd/stim_demo.py` | Stim 最小闭环：`Circuit.generated("repetition_code:memory")` → 探测器采样 |
| `tests/test_stim_demo.py` | 形状、dtype、随机种子确定性 |
| `.github/workflows/ci.yml` | Ubuntu、`pip install -e ".[dev]"`、`pytest -q` |
| `docs/architecture/overview.md` | README 表格（Stim / Tensor QEC / DeltaKit）与仓库阶段映射 |

---

### Task 1: 项目元数据与构建配置

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: 添加 `pyproject.toml`（与下文一致）**

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "qec-rd-software"
version = "0.1.0"
description = "QEC 研发软件：Stim / 张量 QEC / DeltaKit 路线的可扩展 Python 基座（阶段化建设）"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "Apache-2.0" }
dependencies = [
    "numpy>=1.26",
    "stim>=1.14,<2",
]

[project.optional-dependencies]
dev = ["pytest>=8"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "build: add pyproject for qec-rd-software package"
```

---

### Task 2: 包骨架与 Stim 最小闭环

**Files:**
- Create: `src/qec_rd/__init__.py`
- Create: `src/qec_rd/stim_demo.py`

- [ ] **Step 1: 写入 `src/qec_rd/__init__.py`**

```python
"""QEC-RD-Software：量子纠错研发工具链（阶段化交付）。"""

__version__ = "0.1.0"
```

- [ ] **Step 2: 写入 `src/qec_rd/stim_demo.py`**

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add src/qec_rd/__init__.py src/qec_rd/stim_demo.py
git commit -m "feat(qec_rd): add Stim repetition-code detector sampler"
```

---

### Task 3: 单元测试（TDD 验证闭环）

**Files:**
- Create: `tests/test_stim_demo.py`

- [ ] **Step 1: 写入失败测试（若从零开始；若已实现则直接运行通过）**

```python
import numpy as np

from qec_rd.stim_demo import repetition_code_detector_sample


def test_repetition_code_detector_sample_shape_dtype_and_determinism():
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
```

- [ ] **Step 2: 安装可编辑包并运行测试**

Run:

```bash
pip install -e ".[dev]"
pytest tests/test_stim_demo.py -v
```

Expected: `3 passed` 或等价（至少上述用例 PASS）。

- [ ] **Step 3: Commit**

```bash
git add tests/test_stim_demo.py
git commit -m "test: cover repetition-code detector sampler"
```

---

### Task 4: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 写入 workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Test
        run: pytest -q
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: pytest on Python 3.10 and 3.12"
```

---

### Task 5: 架构对照文档

**Files:**
- Create: `docs/architecture/overview.md`

- [ ] **Step 1: 写入文档（README 表格 → 仓库阶段映射）**

内容需说明：Stim 对应 Phase 0；Tensor QEC / DeltaKit 为后续 Epic；目录约定 `src/qec_rd/`、`tests/`、`docs/architecture/`、`docs/superpowers/plans/`。（正文以仓库中实际文件为准。）

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/overview.md
git commit -m "docs: architecture overview vs README pillars"
```

---

### Task 6: 计划归档与 Issue 关联

**Files:**
- Create: `docs/superpowers/plans/2026-04-20-qec-rd-phase0-foundation.md`（本文件）

- [ ] **Step 1: 将本计划纳入版本库**

```bash
git add docs/superpowers/plans/2026-04-20-qec-rd-phase0-foundation.md
git commit -m "docs: add Phase 0 implementation plan"
```

- [ ] **Step 2: 打开 GitHub Issue，粘贴本计划全文或链接到仓库内路径**

使用 `gh issue create --repo QuAIR/QEC-RD-Software --title "..." --body-file ...`（需已登录 `gh`）。

---

## 后续工作（另行开 Issue，不在本计划内验收）

- **Tensor QEC 集成**：评估 `doc/tensorQEC/` 与上游包，定义可选依赖与子包边界。
- **DeltaKit 对齐**：评估 `doc/deltakit/` 与 DEM→控制流水 API，定义适配层。
- **解码与 FTQC / 资源估计**：在 Stim DEM 与采样稳定后，引入解码器与评估流水线。

---

## Self-review（计划作者自检）

1. **Spec coverage（README）：** Phase 0 覆盖「统一 Python 基座 + Stim 范式闭环」；完整「码综合→噪声→混合仿真→解码」留待后续 Epic，已在「后续工作」列出。
2. **Placeholder scan：** 无 TBD/TODO 步骤；代码块与仓库一致。
3. **Consistency：** 包名 `qec-rd-software`、导入 `qec_rd`、版本 `0.1.0` 在各处一致。
