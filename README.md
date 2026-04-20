# QEC 研发软件（QEC-RD-Software）

本项目面向 **量子纠错（QEC）** 全栈研发：从纠错码与电路生成、贴近硬件的噪声建模、大规模高效模拟，到复杂解码与容错分析，为团队提供从 **理论研究** 走向 **工程化研究与部署** 的连贯工具链。

## 目标

构建可对接真实物理硬件的 QEC 研发基座，使科研与工程团队能够：

- 在统一平台上完成「码设计 → 噪声注入 → 仿真评估 → 解码与 FTQC/资源估计」；
- 将探测器级错误模型（DEM）与底层控制、实验配置更紧密地衔接，缩短从理论探索到工程级容错的迭代周期。

## 技术路线

技术架构吸收并融合 **Stim**、**Tensor QEC**、**DeltaKit** 等优势，力求形成「码综合生成 → 真实噪声注入 → 混合仿真 → 多维解码与 FTQC 估计」的闭环：

| 组件 | 角色 |
|------|------|
| **Stim** | 以稳定子电路 / DEM 范式为高速底座，支撑大规模电路与采样的极速评估 |
| **Tensor QEC** | 面向复杂相干等非 Pauli 误差与张量网络类方法，补充纯 stabilizer / Pauli 通道之外的建模能力 |
| **DeltaKit** | 对齐对标其核心能力，强化 DEM 与底层控制指令、实验流水之间的衔接 |

平台以 **Stim** 范式支撑大规模稳定子体系的快速迭代；在需要时引入 **Tensor QEC** 侧的张量与扩展噪声建模；并对齐 **DeltaKit** 所代表的「从错误模型到执行层」的一体化思路，将核心 DEM 语义贯通至分析与部署环节。

## 成员

- [shunzgim](https://github.com/shunzgim)
- [Chriskmh](https://github.com/Chriskmh)
- [LeiZhang-116-4](https://github.com/LeiZhang-116-4)

## 协作

问题与任务跟踪见 [Issues](https://github.com/QuAIR/QEC-RD-Software/issues)。

## 许可证

本项目采用 **Apache License 2.0**，全文见 [LICENSE](LICENSE)；版权说明见 [NOTICE](NOTICE)。
