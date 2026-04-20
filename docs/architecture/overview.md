# 架构对照（README 愿景 → 仓库落地）

README 描述的闭环为：**码综合生成 → 真实噪声注入 → 混合仿真 → 多维解码与 FTQC 估计**。当前仓库采用分阶段交付；本文件记录各组件与 README 表格的映射及目录约定。

## 组件映射

| README 组件 | 角色（摘录） | 仓库阶段 |
|-------------|--------------|----------|
| **Stim** | 稳定子电路 / DEM / 高速采样 | **Phase 0**：`qec_rd.stim_demo` 与 `stim` 依赖；后续扩展至自定义电路与 DEM 流水线 |
| **Tensor QEC** | 非 Pauli / 张量网络类扩展 | **后续 Epic**：可选依赖与子包（不在 Phase 0 强制引入）；参考 `doc/tensorQEC/` 上游资料 |
| **DeltaKit** | DEM 与控制/实验流水衔接 | **后续 Epic**：对接 `doc/deltakit/` 能力或独立绑定层 |

## 目录约定（演进中）

- `src/qec_rd/`：对外 Python API。
- `tests/`：pytest。
- `docs/architecture/`：架构说明。
- `docs/superpowers/plans/`：实现计划归档。
